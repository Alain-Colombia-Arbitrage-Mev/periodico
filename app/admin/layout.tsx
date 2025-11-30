import AdminLayoutClient from './AdminLayoutClient';

export const runtime = 'edge';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AdminLayoutClient>{children}</AdminLayoutClient>;
}
