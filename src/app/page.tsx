import { getCategories, getProducts } from "@/lib/catalog";
import { HomeView } from "@/components/pharmacy/HomeView";

// Regenerate the static home page at most every 5 minutes (ISR) — the page
// ships with all catalog data in the HTML, so first paint has real content
// instead of an empty shell waiting on JS + API round trips.
export const revalidate = 300;

export default async function Home() {
  const [categories, featured, popular] = await Promise.all([
    getCategories(),
    getProducts({ featured: true, limit: 8 }),
    getProducts({ sort: "rating", limit: 8 }),
  ]);

  return (
    <HomeView
      initial={{
        categories,
        featured,
        popular,
      }}
    />
  );
}
