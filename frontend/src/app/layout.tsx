import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClinicalTrials.gov Query Agent",
  description:
    "Ask natural language questions about clinical trials and get structured visualizations.",
};

// Next.js's dev server builds parallel-route missingSlots as a Set and puts it on
// the RSC payload's `m` key (next/dist/server/app-render/app-render.js:971). React 19's
// dev-mode serialization check catches this and pops the overlay, but the app itself
// is fine. Unfixed in Next 15.1–16.2. Next's intercept-console-error calls
// handleConsoleError → overlay before forwarding to the origin console, so we wrap the
// function itself and early-return on specific messages to suppress the overlay. Injected
// inline so it runs before hydration, and reapplied for a few seconds to survive Next's
// own patchConsoleError.
const CONSOLE_ERROR_FILTER = `
(function(){
  if (typeof window === 'undefined') return;
  // React replay reconstructs args as a %c%s%c styling prefix + message
  // (near react-server-dom-webpack-client.browser.dev.js). So looking at args[0] alone
  // can miss depending on the shape — scan every string arg.
  var SIGNATURES = [
    'Only plain objects can be passed to Client Components from Server Components',
    'Set objects are not supported'
  ];
  function shouldDrop(args){
    for (var i = 0; i < args.length; i++) {
      var a = args[i];
      if (typeof a !== 'string') continue;
      for (var j = 0; j < SIGNATURES.length; j++) {
        if (a.indexOf(SIGNATURES[j]) >= 0) return true;
      }
    }
    return false;
  }
  function wrap(){
    var current = window.console && window.console.error;
    if (!current || current.__ctgovFiltered) return;
    var filtered = function(){
      if (shouldDrop(arguments)) return;
      return current.apply(window.console, arguments);
    };
    filtered.__ctgovFiltered = true;
    window.console.error = filtered;
  }
  wrap();
  var tries = 0;
  var iv = setInterval(function(){ wrap(); if (++tries > 40) clearInterval(iv); }, 50);
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {process.env.NODE_ENV !== "production" && (
          <script dangerouslySetInnerHTML={{ __html: CONSOLE_ERROR_FILTER }} />
        )}
      </head>
      <body className="min-h-screen bg-surface text-neutral-100 antialiased">{children}</body>
    </html>
  );
}
