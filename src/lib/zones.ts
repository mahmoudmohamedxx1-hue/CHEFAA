// Shared delivery zones for The Pharmacy
export interface Zone { id: string; nameEn: string; nameAr: string; fee: number; eta: string }

export const ZONES: Zone[] = [
  { id: 'nasr-city', nameEn: 'Nasr City', nameAr: 'مدينة نصر', fee: 30, eta: 'same-day' },
  { id: 'maadi', nameEn: 'Maadi', nameAr: 'المعادي', fee: 30, eta: 'same-day' },
  { id: 'heliopolis', nameEn: 'Heliopolis', nameAr: 'مصر الجديدة', fee: 30, eta: 'same-day' },
  { id: 'zamalek', nameEn: 'Zamalek', nameAr: 'الزمالك', fee: 35, eta: 'same-day' },
  { id: 'downtown', nameEn: 'Downtown Cairo', nameAr: 'وسط البلد', fee: 35, eta: 'same-day' },
  { id: 'new-cairo', nameEn: 'New Cairo', nameAr: 'القاهرة الجديدة', fee: 45, eta: 'next-day' },
  { id: 'sheikh-zayed', nameEn: 'Sheikh Zayed', nameAr: 'الشيخ زايد', fee: 45, eta: 'next-day' },
  { id: 'giza', nameEn: 'Giza', nameAr: 'الجيزة', fee: 40, eta: 'next-day' },
  { id: '6th-october', nameEn: '6th of October', nameAr: '6 أكتوبر', fee: 45, eta: 'next-day' },
  { id: 'alexandria', nameEn: 'Alexandria', nameAr: 'الإسكندرية', fee: 70, eta: '2-3 days' },
  { id: 'mansoura', nameEn: 'Mansoura', nameAr: 'المنصورة', fee: 70, eta: '2-3 days' },
  { id: 'tanta', nameEn: 'Tanta', nameAr: 'طنطا', fee: 70, eta: '2-3 days' },
  { id: 'asyut', nameEn: 'Asyut', nameAr: 'أسيوط', fee: 80, eta: '3-4 days' },
  { id: 'luxor', nameEn: 'Luxor', nameAr: 'الأقصر', fee: 90, eta: '3-4 days' },
  { id: 'aswan', nameEn: 'Aswan', nameAr: 'أسوان', fee: 95, eta: '3-5 days' },
]

export const FREE_DELIVERY_THRESHOLD = 500

export function zoneById(id: string) {
  return ZONES.find((z) => z.id === id)
}

export const ORDER_STATUSES = ['pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'] as const
