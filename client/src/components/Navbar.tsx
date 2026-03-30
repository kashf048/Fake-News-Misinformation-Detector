/**
 * Navbar Component
 */

import { Link, useLocation } from 'wouter';
import { Button } from '@/components/ui/button';
import { Brain, Menu, X } from 'lucide-react';
import { useState } from 'react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [location] = useLocation();

  const isActive = (path: string) => location === path;

  return (
    <nav className="sticky top-0 z-50 bg-background border-b border-border shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/">
            <div className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-2 rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <span className="font-bold text-lg hidden sm:inline">
                Fake News Detector
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <Link href="/">
              <a
                className={`transition-colors ${
                  isActive('/') 
                    ? 'text-blue-600 font-semibold' 
                    : 'text-foreground hover:text-blue-600'
                }`}
              >
                Analyze
              </a>
            </Link>
            <Link href="/history">
              <a
                className={`transition-colors ${
                  isActive('/history') 
                    ? 'text-blue-600 font-semibold' 
                    : 'text-foreground hover:text-blue-600'
                }`}
              >
                History
              </a>
            </Link>
            <Link href="/analytics">
              <a
                className={`transition-colors ${
                  isActive('/analytics') 
                    ? 'text-blue-600 font-semibold' 
                    : 'text-foreground hover:text-blue-600'
                }`}
              >
                Analytics
              </a>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 hover:bg-secondary rounded-lg transition-colors"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden mt-4 space-y-2 pb-4">
            <Link href="/">
              <a
                className={`block px-4 py-2 rounded-lg transition-colors ${
                  isActive('/') 
                    ? 'bg-blue-100 text-blue-600 font-semibold' 
                    : 'hover:bg-secondary'
                }`}
                onClick={() => setIsOpen(false)}
              >
                Analyze
              </a>
            </Link>
            <Link href="/history">
              <a
                className={`block px-4 py-2 rounded-lg transition-colors ${
                  isActive('/history') 
                    ? 'bg-blue-100 text-blue-600 font-semibold' 
                    : 'hover:bg-secondary'
                }`}
                onClick={() => setIsOpen(false)}
              >
                History
              </a>
            </Link>
            <Link href="/analytics">
              <a
                className={`block px-4 py-2 rounded-lg transition-colors ${
                  isActive('/analytics') 
                    ? 'bg-blue-100 text-blue-600 font-semibold' 
                    : 'hover:bg-secondary'
                }`}
                onClick={() => setIsOpen(false)}
              >
                Analytics
              </a>
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
