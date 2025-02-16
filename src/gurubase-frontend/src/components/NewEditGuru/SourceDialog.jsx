import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import * as React from "react";

import MonacoUrlEditor from "@/components/NewEditGuru/MonacoUrlEditor";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { isValidUrl } from "@/utils/common";

import { UrlTableContent } from "./UrlTableContent";

const Dialog = DialogPrimitive.Root;
const DialogPortal = DialogPrimitive.Portal;
const DialogClose = DialogPrimitive.Close;

const StyledDialogContent = React.forwardRef(
  ({ children, isMobile, ...props }, ref) => (
    <DialogPortal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
      <DialogPrimitive.Content
        ref={ref}
        className={cn(
          "fixed z-[100] bg-white shadow-lg transition ease-in-out data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:duration-300 data-[state=open]:duration-500",
          isMobile
            ? "inset-x-0 bottom-0 z-[100] h-[90vh] w-full rounded-t-[20px] data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom"
            : "right-0 top-0 z-[100] h-full w-full max-w-5xl data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right"
        )}
        {...props}>
        {children}
      </DialogPrimitive.Content>
    </DialogPortal>
  )
);

StyledDialogContent.displayName = "StyledDialogContent";

const SourceDialog = React.memo(
  ({
    isOpen,
    onOpenChange,
    title,
    sourceType,
    editorContent,
    onEditorChange,
    clickedSource,
    initialActiveTab,
    selectedUrls,
    setSelectedUrls,
    onAddUrls,
    form,
    isMobile,
    setDirtyChanges,
    setClickedSource,
    setSources,
    handleDeleteUrls
  }) => (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) {
          if (editorContent.trim()) {
            const urls = editorContent
              .split("\n")
              .map((url) => url.trim())
              .filter((url) => url && isValidUrl(url));

            const uniqueUrls = [...new Set(urls)];

            if (uniqueUrls.length > 0) {
              const newUrls = uniqueUrls.map((url) => ({
                id: url,
                type: sourceType,
                url: url,
                status: "NOT_PROCESSED",
                newAddedSource: true
              }));

              onAddUrls(newUrls);
              form.setValue(`${sourceType}Links`, [
                ...(form.getValues(`${sourceType}Links`) || []),
                ...newUrls.map((url) => url.url)
              ]);
            }
          }
          setTimeout(() => {
            document.body.style.pointerEvents = "";
          }, 500);
        } else {
          document.body.style.pointerEvents = "none";
        }
        onOpenChange(open);
      }}>
      <StyledDialogContent isMobile={isMobile}>
        <div className="flex flex-col h-full overflow-hidden">
          <div className="guru-sm:hidden guru-md:flex guru-lg:flex px-5 py-6 items-center gap-5 border-b border-gray-85 bg-gray-25 sticky top-0 z-10">
            <div className="flex-grow">
              <h2 className="text-h5 font-semibold mb-1">
                {clickedSource?.length > 0 ? `Edit ${title}` : `Add ${title}`}
              </h2>
            </div>
            <DialogClose asChild>
              <Button size="icon" variant="ghost">
                <X className="h-6 w-6 text-gray-400" />
                <span className="sr-only">Close</span>
              </Button>
            </DialogClose>
          </div>

          <div className="flex-1 overflow-hidden p-4">
            {clickedSource?.length === 0 ? (
              <MonacoUrlEditor
                placeholder={`Add multiple ${title} with a new line`}
                title={`${title}`}
                tooltipText={`Add multiple ${title} with a new line`}
                value={editorContent}
                onChange={onEditorChange}
              />
            ) : (
              <div className="h-full">
                <UrlTableContent
                  clickedSource={clickedSource}
                  initialActiveTab={initialActiveTab}
                  selectedUrls={selectedUrls}
                  setSelectedUrls={setSelectedUrls}
                  onDeleteUrls={(urls) => {
                    handleDeleteUrls({
                      urlIds: urls,
                      sourceType,
                      setSources,
                      setDirtyChanges,
                      clickedSource,
                      setClickedSource,
                      onOpenChange,
                      form
                    });
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </StyledDialogContent>
    </Dialog>
  )
);

SourceDialog.displayName = "SourceDialog";

export default SourceDialog;
