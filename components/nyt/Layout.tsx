'use client';

import NYTHeader from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

export default function NYTLayout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-white">
      <NYTHeader />
      {children}
    </div>
  );
}

