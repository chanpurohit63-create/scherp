import type { Metadata } from "next";
import Script from "next/script";
import { Orbitron, Roboto_Mono, Inter, Poppins } from "next/font/google";
import "./globals.css";

const orbitron = Orbitron({
  variable: "--font-orbitron",
  subsets: ["latin"],
  weight: ["400", "700", "900"],
});

const robotoMono = Roboto_Mono({
  variable: "--font-roboto-mono",
  subsets: ["latin"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://neuronailab.in";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "NeuronAI Labs - AI-Powered Healthcare Solutions | Healthcare AI",
  description: "Professional IT company offering AI, automation, cloud computing, and cybersecurity services with cutting-edge technology solutions for healthcare.",
  keywords: ["healthcare AI", "artificial intelligence", "medical technology", "AI solutions", "healthcare automation", "cloud computing", "cybersecurity", "IT services"],
  authors: [{ name: "NeuronAI Labs" }],
  creator: "NeuronAI Labs",
  robots: "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "NeuronAI Labs - AI-Powered Healthcare Solutions",
    description: "Empowering doctors and patients with real-time insights, personalized care, and smarter decisions.",
    url: siteUrl,
    siteName: "NeuronAI Labs",
    type: "website",
    locale: "en_US",
    images: [
      {
        url: "/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "NeuronAI Labs - Healthcare AI Solutions",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "NeuronAI Labs - AI-Powered Healthcare",
    description: "Empowering doctors and patients with real-time insights, personalized care, and smarter decisions.",
    creator: "@neuronailabs",
  },
  verification: {
    google: "google-site-verification-code",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const gaId = process.env.NEXT_PUBLIC_GA_ID;

  return (
    <html
      lang="en"
      className={`${orbitron.variable} ${robotoMono.variable} ${inter.variable} ${poppins.variable} h-full antialiased scroll-smooth`}
    >
      <head>
        {/* Google Analytics */}
        {gaId && (
          <>
            <Script
              strategy="afterInteractive"
              src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
            />
            <Script
              id="google-analytics"
              strategy="afterInteractive"
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag('js', new Date());
                  gtag('config', '${gaId}', {
                    page_path: window.location.pathname,
                  });
                `,
              }}
            />
          </>
        )}
      </head>
      <body className="min-h-full flex flex-col bg-dark text-foreground font-inter">{children}</body>
    </html>
  );
}
