import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClinicalTrials.gov Query Agent",
  description:
    "Ask natural language questions about clinical trials and get structured visualizations.",
};

// Next.js dev 서버가 parallel-route missingSlots를 Set으로 만들어 RSC payload의
// `m` 키에 실어 보낸다(next/dist/server/app-render/app-render.js:971). React 19
// dev-mode 직렬화 검사가 이를 잡아 overlay를 띄우는데 앱 동작엔 영향 없다.
// Next 15.1~16.2에서 미수정. Next의 intercept-console-error가 handleConsoleError→
// overlay를 먼저 호출한 뒤 origin으로 넘기므로, 그 함수 자체를 감싸 특정 메시지면
// 조기 return해야 overlay가 안 뜬다. 인라인 스크립트로 초기 하이드레이션 이전에
// 실행 + 초반 몇 초 동안 재적용해서 Next patchConsoleError 이후에도 확실히 잡는다.
const CONSOLE_ERROR_FILTER = `
(function(){
  if (typeof window === 'undefined') return;
  // React replay는 args를 %c%s%c 스타일링 프리픽스 + 메시지 형태로 재구성한다
  // (react-server-dom-webpack-client.browser.dev.js 근처). 따라서 args[0]만 봐선
  // shape에 따라 놓칠 수 있어, 모든 문자열 인자를 스캔한다.
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
