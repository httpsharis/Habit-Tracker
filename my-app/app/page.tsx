import Background from "@/components/Background";
import ChatConsole from "@/components/ChatConsole";
import Header from "@/components/Header";
import Navigation from "@/components/Navigation";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center relative">
      <Background />
      <Header />
      <Navigation />
      <ChatConsole />

      {/* Footer */}
      <footer className="absolute bottom-4 text-center text-xs text-slate-600">
        <p>HabitOS v2.0 • ML-Powered Personal Analytics</p>
      </footer>
    </main>
  );
}