import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Company Brain Workbench",
  description: "Full-stack AI employee workbench where human corrections become reusable company knowledge.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
