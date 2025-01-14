<div align="center">
    <img src="https://pbs.twimg.com/profile_banners/1828170456110682112/1725545674/1500x500" alt="Gurubase Image" /><br/>
</div>


<div align="center">

[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/9CMRSQPqx6)
[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?style=for-the-badge&logo=x&logoColor=white)](https://twitter.com/gurubaseio)
[![Mastodon](https://img.shields.io/badge/Mastodon-%236364FF.svg?style=for-the-badge&logo=mastodon&logoColor=white)](https://mastodon.social/@gurubaseio)
[![Bluesky](https://img.shields.io/badge/Bluesky-%230285FF.svg?style=for-the-badge&logo=bluesky&logoColor=white)](https://bsky.app/profile/gurubase.bsky.social)

</div>

# Gurubase

- [What is Gurubase](#what-is-gurubase)
- [Installation](#installation-self-hosted)
- [How to Create a Guru](#how-to-create-a-guru)
- [How to Claim a Guru](#how-to-claim-a-guru)
- [Showcase Your Guru](#showcase-your-guru)
- [How to Update Datasources](#how-to-update-datasources)
- [License](#license)
- [Help](#help)
- [Used By](#used-by)

## What is Gurubase

[Gurubase](https://gurubase.io) lets you create AI-powered Q&A assistants for any topic or need. Create a new Guru by uploading webpages, PDFs, videos, or GitHub repositories. Start asking questions directly on Gurubase.io, or [embed it on your website](https://github.com/Gurubase/gurubase-widget) to let your users ask questions about your product. It’s already being [used by](#used-by) hundreds of open-source repositories.

## Installation (Self-hosted)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) `19.0.3` or later.
- [Docker Compose](https://docs.docker.com/compose/install/) (`docker compose` or `docker-compose`) `2.6.1` or later.
- OpenAI API key (for text generation and embeddings). Get it from [here](https://platform.openai.com/api-keys).
- Firecrawl API key (for website scraping). Get it from [here](https://www.firecrawl.dev/app/api-keys).

### Quick Install

Run this command to install Gurubase:

```bash
curl -fsSL https://raw.githubusercontent.com/Gurubase/gurubase/refs/heads/selfhosted/gurubase.sh -o gurubase.sh
bash gurubase.sh
```

The installer will:
1. Create a `.gurubase` directory in your home folder
2. Prompt for required API keys
3. Download and start all necessary services
4. Open the web interface at http://localhost:8029

### Upgrade

You can upgrade to the latest version by running the following command:

```bash
curl -sSL https://raw.githubusercontent.com/Gurubase/gurubase/refs/heads/selfhosted/gurubase.sh -o gurubase.sh
bash gurubase.sh upgrade
```

### Remove

You can remove Gurubase by running the following command. This will remove the containers and networks but keep the data files.

```bash
curl -sSL https://raw.githubusercontent.com/Gurubase/gurubase/refs/heads/selfhosted/gurubase.sh -o gurubase.sh
bash gurubase.sh rm
```

### System Requirements

- **Operating System**
  - macOS 10.15 Catalina or later
  - Linux (Ubuntu 20.04 LTS, Debian 10, CentOS 8 or later)
  - ⚠️ Native Windows is not supported, but you can use WSL2 to run Gurubase on Windows.

- **Processor**
  - Quad-core CPU (4 cores) at 2.5 GHz or higher
  - ARM-based processors supported (e.g., Apple M1, M2, M3, etc.)

- **Memory and Storage**
  - 8GB RAM minimum recommended
  - 10GB available disk space (SSD preferred for better performance)

- **Network**
  - Ports 8028 and 8029 must be available

> [!NOTE]
> Only Linux and MacOS are supported at the moment. Native Windows is not supported, but you can use WSL2 to run Gurubase on Windows.

### Services

The following services are installed as part of Gurubase:

| Service | Version | Description |
|---------|---------|-------------|
| Milvus | v2.4.17 | Vector database for storing and searching embeddings |
| RabbitMQ | 3.13.7 | Message broker for task queue management |
| PostgreSQL | 16.3 | Main database for storing application data |
| Redis | 7.2.6 | In-memory data store for caching, rate limiting, and session management |
| Nginx | 1.23.3 | Web server for routing and serving static files |
| Gurubase Backend | latest | [Django](https://www.djangoproject.com/) based backend application |
| Gurubase Frontend | latest | [Next.js](https://nextjs.org/) based frontend application |
| Celery Workers | latest | Background task processors (2 workers) |
| Celery Beat | latest | Periodic task scheduler |

### Data Storage

All data is stored locally in `~/.gurubase/`:
- PostgreSQL data: `~/.gurubase/postgres/`
- Milvus data: `~/.gurubase/milvus/`
- Redis data: `~/.gurubase/redis/`
- Media files: `~/.gurubase/backend_media/`
- Environment variables: `~/.gurubase/.env`

### Backend Django Admin Access

You can access the Django admin interface with the following credentials:

| URL | Email | Password |
|----------|------------------------|----------|
| `http://localhost:8028/admin` | `root@gurubase.io` | `ChangeMe` |

After logging in, you can change the admin password from `http://localhost:8028/admin/password_change/`.

> [!WARNING]
> This interface is intended for advanced users only. Be cautious when making changes as they can affect your Gurubase installation.

### Telemetry

By default, Gurubase collects anonymous telemetry data using [PostHog](https://posthog.com/) to help improve the product. You can opt out of telemetry by following these steps:

1. Edit the frontend environment file `~/.gurubase/.env.frontend`:
```text
NEXT_PUBLIC_TELEMETRY_ENABLED=false
```

2. Recreate the frontend service to apply the new environment:
```bash
cd ~/.gurubase && docker compose up -d --force-recreate frontend
```

## Gurubase Cloud vs Self-hosted

Here's a detailed comparison between Gurubase Cloud and Self-hosted versions:

| Feature | Gurubase Cloud | Self-hosted |
|---------|---------------|-------------|
| Authentication | ✅ Google & GitHub via Auth0 | ❌ Not available |
| Reranking | ✅ Advanced reranking for better results | ❌ Basic ranking via LLM (Custom reranker support coming soon) |
| OG Image Generation | ✅ Automatic generation | ❌ Not available |
| StackOverflow Integration | ✅ Tag-based Q&A scraping | ❌ Not available |
| API Support | ✅ Full API access | ✅ Full API access |
| Binge History | ✅ Follow-up questions & learning graph | ✅ Follow-up questions & learning graph |
| Knowledge Base Sources | ✅ Websites, YouTube, PDFs | ✅ Websites, YouTube, PDFs |
| GitHub Codebase Indexing | ✅ Available | ✅ Available |
| Website Widget | ✅ Available | ✅ Available |
| Base LLM | ✅ OpenAI GPT-4o | ✅ OpenAI GPT-4o |

## How to Create a Guru

Currently, only the Gurubase team can create a Guru. Please open an issue on this repository with the title "Guru Creation Request" and include the GitHub repository link in the issue content. We prioritize Guru creation requests from the maintainers of the tools. Please mention whether you are the maintainer of the tool. If you are not the maintainer, it would be helpful to obtain the maintainer's permission before opening a creation request for the tool.

## How to Claim a Guru

Although you can't create a Guru, you can manage it on Gurubase. For example, you can add, remove, or reindex the datasources. To claim a Guru, you must have a Gurubase account and be one of the tool's maintainers. Please open an issue with the title "Guru Claim Request". Include the link to the Guru (e.g., `https://gurubase.io/g/anteon`), your Gurubase username, and a link proving you are one of the maintainers of the tool, such as a PR merged by you.

## Showcase Your Guru

### 1. Widget

Add an "Ask AI" widget to your website by importing a [small JS script](https://github.com/gurubase/gurubase-widget). For an example, check the [Anteon docs](https://getanteon.com/docs/).

<img src="imgs/widget_demo.gif" alt="Gurubase Widget Demo"/><br/>

### 2. Badge

Like hundreds of GitHub repositories, add a badge to your README to guide your users to learn about your tool on Gurubase.

[Example Badge:](https://github.com/opencost/opencost)
```
[![Gurubase](https://img.shields.io/badge/Gurubase-Ask%20OpenCost%20Guru-006BFF)](https://gurubase.io/g/opencost)
```

<img src="imgs/badge_sample.png" alt="Gurubase Image" width="500"/><br/>

## How to Update Datasources

Datasources can include your tool's documentation webpages, YouTube videos, or PDF files. You can add new ones, remove existing ones, or reindex them. Reindexing ensures your Guru is updated based on changes to the indexed datasources. For example, if you update your tool's documentation, you can reindex those pages so your Guru generates answers based on the latest data.

Once you claim your Guru, you will see your Gurus in the "My Gurus" section.

<img src="imgs/image.png" alt="Gurubase Image" width="300"/><br/>

Click the Guru you want to update. On the edit page, click "Reindex" for the datasource you want to reindex.

<img src="imgs/image-1.png" alt="Gurubase Image" width="720"/><br/>

You can also see the "Last Index Date" on the URL pages.

<img src="imgs/image-2.png" alt="Gurubase Image" width="720"/><br/>

## License

All the content generated by Gurubase aligns with the license of the datasources used to generate answers. More details can be found on the [Terms of Usage](https://gurubase.io/terms-of-use) page, Section 2.

## Help

We prefer Discord for written communication. [Join our channel!](https://discord.gg/9CMRSQPqx6) To stay updated on new features, you can follow us on [X](https://x.com/gurubaseio), [Mastodon](https://mastodon.social/@gurubaseio), and [Bluesky](https://bsky.app/profile/gurubase.bsky.social).

## Used By

Gurubase currently hosts **hundreds** of Gurus, and it grows every day. Here are some repositories that showcase their Gurus in their READMEs or documentation.

<table>

<tr>

  <td align="center">
    <a href="https://github.com/LizardByte/Sunshine/">
      <img src="https://raw.githubusercontent.com/LizardByte/Sunshine/master/sunshine.png" width="40" height="40">
      <br>
      <b>Sunshine</b>
      <br>
      <b>21.7K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/teableio/teable">
      <img src="https://avatars.githubusercontent.com/u/113977713?s=48&v=4" width="40" height="40">
      <br>
      <b>Teable</b>
      <br>
      <b>15K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/albumentations-team/albumentations">
      <img src="https://avatars.githubusercontent.com/u/57894582?s=48&v=4" width="40" height="40">
      <br>
      <b>Albumentations</b>
      <br>
      <b>14.5K ★</b>
    </a>
  </td>


  <td align="center">
    <a href="https://github.com/openimsdk/open-im-server">
      <img src="https://avatars.githubusercontent.com/u/84842645?s=48&v=4" width="40" height="40">
      <br>
      <b>Open IM</b>
      <br>
      <b>14.3K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/sandboxie-plus/Sandboxie">
      <img src="https://avatars.githubusercontent.com/u/63755826?s=48&v=4" width="40" height="40">
      <br>
      <b>Sandboxie</b>
      <br>
      <b>14.2K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/quarkusio/quarkus">
      <img src="https://avatars.githubusercontent.com/u/47638783?s=48&v=4" width="40" height="40">
      <br>
      <b>Quarkus</b>
      <br>
      <b>14K ★</b>
    </a>
  </td>

  <td  align="center">
    <a href="https://github.com/navidrome/navidrome">
      <img src="https://avatars.githubusercontent.com/u/26692192?s=48&v=4" width="40" height="40">
      <br>
      <b>Navidrome</b>
      <br>
      <b>12.9K ★</b>
    </a>
  </td>

</tr>

<tr>

  <td  align="center">
    <a href="https://github.com/vanna-ai/vanna">
      <img src="https://avatars.githubusercontent.com/u/132533812?s=48&v=4" width="40" height="40">
      <br>
      <b>Vanna</b>
      <br>
      <b>12.6K ★</b>
    </a>
  </td>

  <td  align="center">
    <a href="https://github.com/tamagui/tamagui">
      <img src="https://avatars.githubusercontent.com/u/94025540?s=48&v=4" width="40" height="40">
      <br>
      <b>Tamagui</b>
      <br>
      <b>11.9K ★</b>
    </a>
  </td>

  <td  align="center">
    <a href="https://github.com/carla-simulator/carla">
      <img src="https://avatars.githubusercontent.com/u/33029185?s=48&v=4" width="40" height="40">
      <br>
      <b>Carla</b>
      <br>
      <b>11.9K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/duplicati/duplicati">
      <img src="https://avatars.githubusercontent.com/u/8270231?s=48&v=4" width="40" height="40">
      <br>
      <b>Duplicati</b>
      <br>
      <b>11.5K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/cesanta/mongoose">
      <img src="https://avatars.githubusercontent.com/u/5111322?s=48&v=4" width="40" height="40">
      <br>
      <b>Mongoose</b>
      <br>
      <b>11.3K ★</b>
    </a>
  </td>

  <td  align="center">
    <a href="https://github.com/assimp/assimp">
      <img src="https://avatars.githubusercontent.com/u/265533?s=48&v=4" width="40" height="40">
      <br>
      <b>Assimp</b>
      <br>
      <b>11.2K ★</b>
    </a>
  </td>

  <td  align="center">
    <a href="https://github.com/Nozbe/WatermelonDB">
      <img src="https://gurubase.io/_next/image?url=https%3A%2F%2Fs3.eu-central-1.amazonaws.com%2Fanteon-strapi-cms-wuby8hpna3bdecoduzfibtrucp5x%2Fwatermelon_logo_83e295693d.png&w=96&q=75" width="40" height="40">
      <br>
      <b>WatermelonDB</b>
      <br>
      <b>10.7K ★</b>
    </a>
  </td>
</tr>

<tr>
  <td  align="center">
    <a href="https://github.com/gorse-io/gorse">
      <img src="https://avatars.githubusercontent.com/u/74893108?s=48&v=4" width="40" height="40">
      <br>
      <b>Gorse</b>
      <br>
      <b>8.7K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/sqlfluff/sqlfluff">
      <img src="https://avatars.githubusercontent.com/u/71874918?s=48&v=4" width="40" height="40">
      <br>
      <b>SQLFluff</b>
      <br>
      <b>8.4K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/databendlabs/databend">
      <img src="https://avatars.githubusercontent.com/u/80994548?s=48&v=4" width="40" height="40">
      <br>
      <b>Databend</b>
      <br>
      <b>8.1K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/nhost/nhost">
      <img src="https://avatars.githubusercontent.com/u/48448799?s=48&v=4" width="40" height="40">
      <br>
      <b>Nhost</b>
      <br>
      <b>8K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/ast-grep/ast-grep">
      <img src="https://avatars.githubusercontent.com/u/114017360?s=48&v=4" width="40" height="40">
      <br>
      <b>ast-grep(sg)</b>
      <br>
      <b>7.9K ★</b>
    </a>
  </td>

  <td align="center">
    <a href="https://github.com/py-why/dowhy">
      <img src="https://avatars.githubusercontent.com/u/101266056?s=48&v=4" width="40" height="40">
      <br>
      <b>DoWhy</b>
      <br>
      <b>7.2K ★</b>
    </a>
  </td>

  <td  align="center">
    <b><i>100+ more</i></b>
  </td>
</tr>
</table>