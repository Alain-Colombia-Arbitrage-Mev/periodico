/**
 * NAVIGATION COMPONENT - OPTIMIZED
 * Professional menu with categories, mobile responsive, and animations
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Menu, X, ChevronDown, Search, Bell } from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================
// TYPES
// ============================================
interface Category {
  name: string;
  slug: string;
  color: string;
  icon?: string;
}

// ============================================
// CATEGORIES DATA
// ============================================
const categories: Category[] = [
  { name: 'Política', slug: 'politica', color: 'blue', icon: '🏛️' },
  { name: 'Economía', slug: 'economia', color: 'green', icon: '💰' },
  { name: 'Judicial', slug: 'judicial', color: 'red', icon: '⚖️' },
  { name: 'Internacional', slug: 'internacional', color: 'purple', icon: '🌎' },
  { name: 'Sociedad', slug: 'sociedad', color: 'orange', icon: '👥' },
];

// ============================================
// NAVIGATION COMPONENT
// ============================================
export default function Navigation() {
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close menu on route change
  useEffect(() => {
    setIsMenuOpen(false);
  }, [pathname]);

  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
  }, [isMenuOpen]);

  const getCategoryColor = (color: string) => {
    const colors = {
      blue: 'text-blue-600 hover:bg-blue-50',
      green: 'text-green-600 hover:bg-green-50',
      red: 'text-red-600 hover:bg-red-50',
      purple: 'text-purple-600 hover:bg-purple-50',
      orange: 'text-orange-600 hover:bg-orange-50',
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  const isActive = (slug: string) => {
    return pathname === `/${slug}`;
  };

  return (
    <>
      {/* Top Bar - Estilo La Nación */}
      <div className="top-bar">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 text-xs">
              <span className="text-gray-400">📍 Buenos Aires, Argentina</span>
              <span className="hidden md:inline text-gray-600">|</span>
              <span className="hidden md:inline text-gray-400">
                {new Date().toLocaleDateString('es-AR', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>
            <div className="hidden md:flex items-center gap-4 text-xs">
              <button className="text-gray-400 hover:text-white transition-colors" style={{color: 'var(--ln-blue-primary)'}}>
                <Bell className="w-4 h-4" />
              </button>
              <a href="https://twitter.com/politicaarg" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                Twitter
              </a>
              <a href="https://facebook.com/politicaargentina" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                Facebook
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Main Header - Estilo La Nación */}
      <header
        className={cn(
          'main-header transition-all duration-300',
          isScrolled && 'shadow-sm'
        )}
      >
        <div className="container mx-auto px-4">
          {/* Logo and Actions */}
          <div className="flex items-center justify-between py-3">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded transition-colors"
              aria-label="Toggle menu"
              style={{color: 'var(--ln-neutral-800)'}}
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

            {/* Logo - Estilo La Nación */}
            <Link href="/" className="flex items-center gap-3">
              <div className="w-12 h-12 flex items-center justify-center" style={{backgroundColor: 'var(--ln-blue-primary)'}}>
                <span className="text-white font-bold text-2xl">LA</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="logo-text text-2xl md:text-3xl">
                  Política Argentina
                </h1>
                <p className="text-xs" style={{color: 'var(--ln-neutral-400)'}}>
                  Noticias en tiempo real
                </p>
              </div>
            </Link>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsSearchOpen(!isSearchOpen)}
                className="p-2 hover:bg-gray-100 rounded transition-colors"
                aria-label="Search"
                style={{color: 'var(--ln-neutral-800)'}}
              >
                <Search className="w-5 h-5" />
              </button>
              <Link
                href="/admin"
                className="hidden md:inline-flex items-center gap-2 px-4 py-2 text-white rounded text-sm font-medium transition-colors"
                style={{backgroundColor: 'var(--ln-blue-primary)'}}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--ln-blue-dark)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--ln-blue-primary)'}
              >
                Admin
              </Link>
            </div>
          </div>

          {/* Search Bar */}
          {isSearchOpen && (
            <div className="pb-4 animate-slideDown">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar noticias, temas, personas..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  autoFocus
                />
              </div>
            </div>
          )}

          {/* Desktop Navigation - Estilo La Nación */}
          <nav className="hidden lg:block" style={{borderTop: '1px solid var(--ln-neutral-200)'}}>
            <ul className="flex items-center gap-0">
              <li>
                <Link
                  href="/"
                  className={cn(
                    'nav-link flex items-center gap-2 px-4 py-3 border-b-2 transition-all',
                    pathname === '/'
                      ? 'nav-link-active'
                      : 'border-transparent hover:border-gray-300'
                  )}
                >
                  🏠 <span className="hidden xl:inline">Inicio</span>
                </Link>
              </li>
              {categories.map((category) => (
                <li key={category.slug}>
                  <Link
                    href={`/${category.slug}`}
                    className={cn(
                      'nav-link flex items-center gap-2 px-4 py-3 border-b-2 transition-all',
                      isActive(category.slug)
                        ? 'nav-link-active font-semibold'
                        : 'border-transparent hover:border-gray-300'
                    )}
                  >
                    <span className="lg:hidden xl:inline">{category.icon}</span>
                    <span>{category.name}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden animate-fadeIn"
          onClick={() => setIsMenuOpen(false)}
        />
      )}

      {/* Mobile Menu */}
      <div
        className={cn(
          'fixed top-0 left-0 h-full w-80 bg-white z-50 transform transition-transform duration-300 ease-in-out lg:hidden',
          isMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Mobile Menu Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">PA</span>
              </div>
              <span className="font-bold text-gray-900">Menú</span>
            </div>
            <button
              onClick={() => setIsMenuOpen(false)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Mobile Menu Content */}
          <nav className="flex-1 overflow-y-auto p-4">
            <ul className="space-y-1">
              <li>
                <Link
                  href="/"
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors rounded-lg',
                    pathname === '/'
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-700 hover:bg-gray-50'
                  )}
                >
                  <span className="text-xl">🏠</span>
                  <span>Inicio</span>
                </Link>
              </li>
              {categories.map((category) => (
                <li key={category.slug}>
                  <Link
                    href={`/${category.slug}`}
                    className={cn(
                      'flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors rounded-lg',
                      isActive(category.slug)
                        ? `${getCategoryColor(category.color)} font-semibold`
                        : 'text-gray-700 hover:bg-gray-50'
                    )}
                  >
                    <span className="text-xl">{category.icon}</span>
                    <span>{category.name}</span>
                  </Link>
                </li>
              ))}
            </ul>

            {/* Mobile Menu Footer */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <Link
                href="/admin"
                className="flex items-center justify-center gap-2 w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Admin Panel
              </Link>
            </div>
          </nav>
        </div>
      </div>
    </>
  );
}

