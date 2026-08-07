"use client";
// eslint-disable  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2ZVVkVGVBPT06OGZiOTdmMTc=

import { MainLayout } from "@/components/layout/main-layout";
import { useLanguage } from "@/providers/LanguageProvider";
// eslint-disable  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2ZVVkVGVBPT06OGZiOTdmMTc=

export default function FullstackAnalysisPage() {
  const { t } = useLanguage();

  return (
    <MainLayout title={t("nav.fullstackAnalysis")}>
      <div className="-m-6 h-full">
        <iframe
          src="/gitnexus-web/index.html"
          className="h-full w-full border-0"
          title={t("nav.fullstackAnalysis")}
          allow="fullscreen"
        />
      </div>
    </MainLayout>
  );
}
