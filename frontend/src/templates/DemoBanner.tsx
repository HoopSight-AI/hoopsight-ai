import Link from 'next/link';

import { StickyBanner } from '@/features/landing/StickyBanner';

export const DemoBanner = () => (
  <StickyBanner>
    20% off all premium plans! - 
    {' '}
    <Link href="/sign-up">Buy Now</Link>
  </StickyBanner>
);
