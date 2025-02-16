import re
import os
import discord
import logging
import sys
import aiohttp
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Integration, Thread
from datetime import datetime, timedelta
from asgiref.sync import sync_to_async
from core.utils import create_fresh_binge
import time
from django.core.cache import caches

class Command(BaseCommand):
    help = 'Starts a Discord listener bot'

    def __init__(self):
        super().__init__()
        # Cache timeout in seconds (e.g., 5 minutes)
        # Set to 0 to disable caching
        # This is because dynamic channel updates are not immediately reflected
        # And this may result in bad UX, and false positive bug reports
        self.cache_timeout = 0
        self.prod_backend_url = settings.PROD_BACKEND_URL.rstrip('/')

    def get_trust_score_emoji(self, trust_score):
        score = trust_score / 100.0
        if score >= 0.8:
            return "🟢"  # Green
        elif score >= 0.6:
            return "🟡"  # Yellow
        elif score >= 0.4:
            return "🟡"  # Yellow
        elif score >= 0.2:
            return "🟠"  # Orange
        else:
            return "🔴"  # Red

    def strip_first_header(self, content):
        """Remove the first header (starting with # and ending with newline) from content."""
        if content.startswith('#'):
            # Find the first newline
            newline_index = content.find('\n')
            if newline_index != -1:
                # Return content after the newline
                return content[newline_index + 1:].lstrip()
        return content

    def format_response(self, response):
        formatted_msg = []
        content = self.strip_first_header(response['content'])
        metadata_length = 0
        
        # Calculate space needed for metadata (trust score and references)
        trust_score = response.get('trust_score', 0)
        trust_emoji = self.get_trust_score_emoji(trust_score)
        formatted_msg.append(f"---------\n_**Trust Score**: {trust_emoji} {trust_score}%_")
        
        if response.get('references'):
            formatted_msg.append("_**Sources:**_")
            for ref in response['references']:
                clean_title = re.sub(r':[a-zA-Z0-9_+-]+:|[\U0001F300-\U0001F9FF]', '', ref['title'])
                formatted_msg.append(f"• [_{clean_title}_](<{ref['link']}>)")

        # Add space for frontend link
        formatted_msg.append(f":eyes: [_View on Gurubase for a better UX_]({response['question_url']})")

        metadata_length = sum(len(msg) for msg in formatted_msg)
        
        # Calculate max length for content to stay within Discord's 2000 char limit
        max_content_length = 1900 - metadata_length  # Leave some buffer
        
        # Truncate content if necessary
        if len(content) > max_content_length:
            content = content[:max_content_length-3] + "..."

        formatted_msg.insert(0, content)
        
        return "\n".join(formatted_msg)

    async def get_guru_type_slug(self, integration):
        # Wrap the guru_type access in sync_to_async
        guru_type = await sync_to_async(lambda: integration.guru_type)()
        return await sync_to_async(lambda: guru_type.slug)()

    async def get_api_key(self, integration):
        # Wrap the guru_type access in sync_to_async
        api_key = await sync_to_async(lambda: integration.api_key)()
        return await sync_to_async(lambda: api_key.key)()

    async def get_guild_integration(self, guild_id):
        # Try to get integration from cache first
        cache = caches['alternate']
        cache_key = f"discord_integration:{guild_id}"
        integration = cache.get(cache_key)
        
        if not integration:
            try:
                # If not in cache, get from database
                integration = await sync_to_async(Integration.objects.get)(
                    type=Integration.Type.DISCORD,
                    external_id=guild_id
                )
                # Cache for 5 minutes
                cache.set(cache_key, integration, timeout=self.cache_timeout)
            except Integration.DoesNotExist:
                logging.error(f"No integration found for guild {guild_id}", exc_info=True)
                return None
        
        return integration

    async def get_or_create_thread_binge(self, thread_id, integration, guru_type_object):
        try:
            # Try to get existing thread
            thread = await sync_to_async(Thread.objects.get)(thread_id=thread_id, integration=integration)
            # Get binge asynchronously
            binge = await sync_to_async(lambda: thread.binge)()
            return binge
        except Thread.DoesNotExist:
            # Create new binge and thread without needing a question
            binge = await sync_to_async(create_fresh_binge)(guru_type_object, None)
            await sync_to_async(Thread.objects.create)(
                thread_id=thread_id,
                binge=binge,
                integration=integration
            )
            return binge

    async def stream_answer(self, guru_type, question, api_key, binge_id=None):
        url = f"{self.prod_backend_url}/api/v1/{guru_type}/answer/"
        headers = {
            'X-API-KEY': f'{api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'question': question,
            'stream': True,
            'short_answer': True
        }
        if binge_id:
            payload['session_id'] = str(binge_id)
        
        buffer = ""
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                async for chunk in response.content:
                    if chunk:
                        text = chunk.decode('utf-8')
                        buffer += text
                        if buffer.strip():
                            yield buffer

    async def get_finalized_answer(self, guru_type, question, api_key, binge_id=None):
        url = f"{self.prod_backend_url}/api/v1/{guru_type}/answer/"
        headers = {
            'X-API-KEY': f'{api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'question': question,
            'stream': False,
            'short_answer': True,
            'fetch_existing': True
        }
        if binge_id:
            payload['session_id'] = str(binge_id)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response_json = await response.json()
                if response.status == 200:
                    return response_json, True
                else:
                    print(response_json, type(response_json))
                    return response_json['msg'], False

    async def send_channel_unauthorized_message(
        self,
        message: discord.Message,
        guru_slug: str,
        question: str
    ) -> None:
        """Send a message explaining how to authorize the channel."""
        try:
            settings_url = f"{settings.BASE_URL.rstrip('/')}/guru/{guru_slug}/integrations/discord"
            
            # Create embed for better formatting
            embed = discord.Embed(
                title="❌ Channel Not Authorized",
                description=(
                    "This channel is not authorized to use the bot.\n\n"
                    f"Please visit [Gurubase Settings]({settings_url}) to configure "
                    "the bot and add this channel to the allowed channels list."
                ),
                color=discord.Color.red()  # Red color for error messages
            )
            
            # If in a thread, reply in thread. Otherwise create a thread
            if isinstance(message.channel, discord.Thread):
                await message.channel.send(embed=embed)
            else:
                thread = await message.create_thread(
                    name=f"Q: {question[:50]}...",
                    auto_archive_duration=60  # Archive after 1 hour of inactivity
                )
                await thread.send(embed=embed)
            
        except discord.Forbidden as e:
            logging.error(f"Discord forbidden error while sending unauthorized message: {str(e)}")
        except discord.HTTPException as e:
            logging.error(f"Discord API error while sending unauthorized message: {str(e)}")
        except Exception as e:
            logging.error(f"Error sending unauthorized channel message: {str(e)}")

    def setup_discord_client(self):
        # Setup logging to stdout
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

        # Setup Discord client
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents, connector=None)

        @client.event
        async def on_ready():
            self.stdout.write(self.style.SUCCESS(f'We have logged in as {client.user}'))

        @client.event
        async def on_message(message):
            if message.author == client.user:
                return

            # First check if bot was mentioned
            if client.user not in message.mentions:
                return

            # Then check if we have a valid guild
            guild_id = str(message.guild.id) if message.guild else None
            if not guild_id:
                return

            # Get integration from cache/database
            integration = await self.get_guild_integration(guild_id)
            await sync_to_async(lambda: print(f'integration: {integration}'))()
            if not integration or not await sync_to_async(lambda: integration.access_token)():
                return

            try:
                # Check if the current channel is allowed
                channel_id = str(message.channel.id)
                # If message is from a thread, get the parent channel id
                if isinstance(message.channel, discord.Thread):
                    channel_id = str(message.channel.parent_id)
                
                channels = await sync_to_async(lambda: integration.channels)()
                channel_allowed = False
                question = message.content.replace(f'<@{client.user.id}>', '').strip()

                for channel in channels:
                    if str(channel.get('id')) == channel_id and channel.get('allowed', False):
                        channel_allowed = True
                        break
                
                if not channel_allowed:
                    guru_type_slug = await self.get_guru_type_slug(integration)
                    await self.send_channel_unauthorized_message(
                        message, 
                        guru_type_slug, 
                        question)
                    return

                # Remove the bot mention from the message
                
                # Get guru type slug and API key
                guru_type_slug = await self.get_guru_type_slug(integration)
                api_key = await self.get_api_key(integration)
                guru_type_object = await sync_to_async(lambda: integration.guru_type)()

                # Handle message in thread or create new thread
                try:
                    if message.channel.type == discord.ChannelType.public_thread:
                        # If in thread, send thinking message directly to thread
                        thinking_msg = await message.channel.send("Thinking... 🤔")
                        
                        # Get or create thread and binge
                        binge = await self.get_or_create_thread_binge(
                            str(message.channel.id),
                            integration,
                            guru_type_object
                        )
                        binge_id = binge.id
                    else:
                        # If not in thread, create a thread and send thinking message there
                        thread = await message.create_thread(
                            name=f"Q: {question[:50]}...",  # Use first 50 chars of question as thread name
                            auto_archive_duration=60  # Archive after 1 hour of inactivity
                        )
                        thinking_msg = await thread.send("Thinking... 🤔")
                        
                        # Create new thread and binge
                        binge = await self.get_or_create_thread_binge(
                            str(thread.id),
                            integration,
                            guru_type_object
                        )
                        binge_id = binge.id
                    
                    last_update = time.time()
                    update_interval = 0.5  # Update every 0.5 seconds
                    
                    # First, stream the response
                    async for streamed_content in self.stream_answer(
                        guru_type_slug,
                        question,
                        api_key,
                        binge_id
                    ):
                        current_time = time.time()
                        if current_time - last_update >= update_interval:
                            # Strip header from streamed content
                            cleaned_content = self.strip_first_header(streamed_content)
                            if cleaned_content:
                                cleaned_content += '\n:clock1: _streaming..._'
                                await thinking_msg.edit(content=cleaned_content)
                                last_update = current_time
                    
                    # After streaming is done, fetch the formatted response
                    response, success = await self.get_finalized_answer(
                        guru_type_slug,
                        question,
                        api_key,
                        binge_id
                    )
                    
                    if success:
                        formatted_response = self.format_response(response)
                        await thinking_msg.edit(content=formatted_response)
                    else:
                        error_msg = response if response else "Sorry, I couldn't process your request. 😕"
                        await thinking_msg.edit(content=error_msg)
                        
                except discord.Forbidden as e:
                    logging.error(f"Discord forbidden error occurred: {str(e)}")
                    await thinking_msg.edit(content="❌ I don't have permission to perform this action. Please check my permissions.")
                except discord.HTTPException as e:
                    logging.error(f"Discord API error occurred: {str(e)}")
                    await thinking_msg.edit(content=f"❌ Discord API error occurred")
                except aiohttp.ClientError as e:
                    logging.error(f"Network error occurred while processing your request. {str(e)}")
                    await thinking_msg.edit(content="❌ Network error occurred while processing your request.")
                except Exception as e:
                    logging.error(f"An unexpected error occurred: {str(e)}")
                    await thinking_msg.edit(content=f"❌ An unexpected error occurred.")

            except Exception as e:
                logging.error(f"Error processing Discord message: {str(e)}", exc_info=True)

        return client, handler

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Discord listener...'))
        
        try:
            client, handler = self.setup_discord_client()
            token = settings.DISCORD_BOT_TOKEN
            
            client.run(token, log_handler=handler, log_level=logging.DEBUG)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Shutting down Discord listener...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 