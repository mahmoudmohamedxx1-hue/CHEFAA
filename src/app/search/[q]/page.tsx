import type { Metadata } from "next";
import { CategoryView } from "@/components/pharmacy/CategoryView";

export const metadata: Metadata = {
  title: "Search | The Pharmacy — البحث",
  robots: { index: false },
};

function safeDecode(s: string): string {
  try {
    return decodeURIComponent(s);
  } catch {
    return s;
  }
}

export default async function SearchPage({
  params,
}: {
  params: Promise<{ q: string }>;
}) {
  const { q } = await params;
  return <CategoryView key={q} searchQuery={safeDecode(q)} />;
}
