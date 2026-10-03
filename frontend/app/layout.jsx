import './globals.css';

export const metadata = {
  title: 'Library Management System',
  description: 'Containerized LMS — Book Catalog, Members, Circulation & Notifications',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
