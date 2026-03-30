/**
 * Footer Component
 */

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-secondary border-t border-border mt-12">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* About */}
          <div>
            <h3 className="font-semibold text-lg mb-4">About</h3>
            <p className="text-sm text-muted-foreground">
              Fake News Detector is an AI-powered system that analyzes headlines and images to detect misinformation.
            </p>
          </div>

          {/* Features */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Features</h3>
            <ul className="text-sm text-muted-foreground space-y-2">
              <li>• AI-powered analysis</li>
              <li>• Image verification</li>
              <li>• Fact-checking integration</li>
              <li>• Analytics dashboard</li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Support</h3>
            <p className="text-sm text-muted-foreground">
              For support and feedback, please contact us.
            </p>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-muted-foreground">
            <p>&copy; {currentYear} Fake News Detector. All rights reserved.</p>
            <div className="flex gap-6 mt-4 md:mt-0">
              <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
              <a href="#" className="hover:text-foreground transition-colors">Terms</a>
              <a href="#" className="hover:text-foreground transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
