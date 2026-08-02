import './globals.css';
import React from 'react';
import { Josefin_Sans } from 'next/font/google';
import { AuthProvider } from '@/context/AuthContext';
import AppLayout from '@/components/AppLayout';

const josefin = Josefin_Sans({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-josefin',
});

export const metadata = {
  title: 'Captrix AI - Enterprise Financial Intelligence Platform',
  description: 'Enterprise AI Financial Intelligence Platform for automated accounting workbook analysis, ratio calculations, and business insights.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={josefin.variable} suppressHydrationWarning>
      <body className={`${josefin.className} min-h-screen bg-[#050D1A] antialiased`} suppressHydrationWarning>
        <AuthProvider>
          <AppLayout>{children}</AppLayout>
        </AuthProvider>
      </body>
    </html>
  );
}
