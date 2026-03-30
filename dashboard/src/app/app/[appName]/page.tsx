import { getAppDetail } from '@/lib/db';
import AppDetailClient from '@/components/AppDetailClient';
import { notFound } from 'next/navigation';

export default async function AppDetailPage({ params }: { params: { appName: string } }) {
  const decodedName = decodeURIComponent(params.appName);
  console.log("Fetching details for:", decodedName);
  
  const data = await getAppDetail(decodedName);
  
  if (!data || !data.analytics) {
    return notFound();
  }

  return (
    <main className="min-h-screen bg-[#020202] text-white selection:bg-indigo-500/30 font-sans p-6 md:p-12 relative overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-indigo-600/10 rounded-full blur-[120px] mix-blend-screen pointer-events-none" />
      <div className="absolute top-1/2 left-0 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[180px] mix-blend-screen pointer-events-none" />
      
      <div className="max-w-[1400px] mx-auto relative z-10">
        <AppDetailClient appData={data} appName={decodedName} />
      </div>
    </main>
  );
}
