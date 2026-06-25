import "./globals.css";
import React from "react";

export const metadata = {
  title: "SPS Enterprise AI Proposal Capture Manager",
  description: "Enterprise proposal generation and compliance analysis workspace.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-neutral-950 text-neutral-100">
        <div className="flex flex-col min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
