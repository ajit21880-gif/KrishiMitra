import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KrishiMitra AI - Hyperlocal Mandi Assistant",
  description: "Farmer Mandi price rates and input dealers directory.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="max-w-md mx-auto bg-white min-h-screen shadow-lg flex flex-col relative border-x border-gray-200">
          {children}
        </div>
      </body>
    </html>
  );
}
