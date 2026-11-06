import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { QueryProvider } from "@/components/providers/query-provider";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#071A3A",
};

export const metadata: Metadata = {
  metadataBase: new URL("https://wiyata.sadeyan.my.id"),
  title: {
    default: "WIYATA — Database Learning Center & Professional Reference",
    template: "%s | WIYATA",
  },
  description:
    "Pusat pembelajaran database profesional: SQL query studio interaktif, tantangan lab, katalog 21+ alat observabilitas terverifikasi, dan jalur karier DBA & DBRE.",
  applicationName: "WIYATA",
  authors: [{ name: "WIYATA Team" }],
  keywords: [
    "Database",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "Oracle",
    "SQL Server",
    "IBM Db2",
    "DBA",
    "DBRE",
    "Data Engineer",
    "Database Observability",
    "Control-M",
    "DBeaver",
    "Query Optimization",
  ],
  creator: "WIYATA",
  publisher: "WIYATA",
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  manifest: "/site.webmanifest",
  openGraph: {
    title: "WIYATA — Database Learning Center & Professional Reference",
    description:
      "Pusat pembelajaran database profesional: SQL query studio interaktif, tantangan lab, katalog 21+ alat observabilitas terverifikasi, dan jalur karier DBA & DBRE.",
    url: "https://wiyata.sadeyan.my.id",
    siteName: "WIYATA",
    locale: "id_ID",
    alternateLocale: ["en_US"],
    type: "website",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "WIYATA — Your Database Learning Center",
      },
      {
        url: "/icon-512.png",
        width: 512,
        height: 512,
        alt: "WIYATA App Icon",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "WIYATA — Database Learning Center & Professional Reference",
    description:
      "Pusat pembelajaran database profesional: SQL query studio, tantangan lab interaktif, katalog alat terverifikasi, dan peta jalur profesi.",
    images: ["/og-image.png"],
    creator: "@wiyata",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased min-h-screen w-full overflow-x-hidden bg-[#071A3A]`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <QueryProvider>{children}</QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
