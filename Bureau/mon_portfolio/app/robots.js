import { SITE_URL } from '@/lib/seo';

export const dynamic = 'force-static';

export default function robots() {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/scan-qr/', '/carte-de-visite-divin-ntwali/'],
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
