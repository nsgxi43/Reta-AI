import { Instrument_Sans } from "next/font/google"; // Instrument Sans for a modern, clean look similar to Inter but slightly more unique
import "./globals.css";

const instrumentSans = Instrument_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter", // Re-using variable for simplicity with existing styles
});

export const metadata = {
  title: "Reta.ai - Future of Shopping",
  description: "Experience AI-powered shopping assistance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={instrumentSans.variable}>
      <head>
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"
        />
      </head>
      <body className="antialiased min-h-dvh flex flex-col items-center bg-black sm:justify-center sm:bg-zinc-950">
        <div className="w-full sm:max-w-md h-[100dvh] overflow-hidden relative flex flex-col sm:shadow-2xl sm:border-x sm:border-zinc-800">
           {children}
        </div>
      </body>
    </html>
  );
}
