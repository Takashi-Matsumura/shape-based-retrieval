import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CAD Similarity Search",
  description: "Upload CAD files and search for similar 3D shapes",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className="antialiased">{children}</body>
    </html>
  );
}
