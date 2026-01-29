import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full text-center">
        <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          SEORankPulse
        </h1>
        
        <p className="text-xl text-muted-foreground mb-8">
          The Ultimate AI-Powered SEO Analysis Platform
        </p>
        
        <div className="flex gap-4 justify-center">
          <Link
            href="/auth/login"
            className="px-8 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            Login
          </Link>
          
          <Link
            href="/auth/register"
            className="px-8 py-3 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors"
          >
            Sign Up
          </Link>
        </div>
        
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Advanced Crawler</h3>
            <p className="text-sm text-muted-foreground">
              Async crawling with JavaScript rendering support
            </p>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">AI Analysis</h3>
            <p className="text-sm text-muted-foreground">
              Semantic analysis with Hugging Face transformers
            </p>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Link Graph</h3>
            <p className="text-sm text-muted-foreground">
              Neo4j-powered PageRank calculations
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
