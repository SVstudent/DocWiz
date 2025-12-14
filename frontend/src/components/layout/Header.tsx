'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Debug: Log auth state (remove this later)
  console.log('Header - isAuthenticated:', isAuthenticated, 'user:', user);

  const handleLogout = () => {
    logout();
    // Clear localStorage to be sure
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-storage');
    }
    router.push('/login');
  };

  const navLinks = [
    { href: '/', label: 'Dashboard', requiresAuth: true },
  ];

  const visibleNavLinks = navLinks.filter(
    (link) => !link.requiresAuth || isAuthenticated
  );

  return (
    <header className="sticky top-0 z-50 w-full border-b border-surgical-gray-200 bg-white shadow-sm">
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-surgical-blue-600">
                <span className="text-lg font-bold text-white">D</span>
              </div>
              <span className="text-xl font-bold text-surgical-blue-600">
                DocWiz
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-1">
            {visibleNavLinks.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${isActive
                      ? 'bg-surgical-blue-50 text-surgical-blue-600'
                      : 'text-surgical-gray-700 hover:bg-surgical-gray-50 hover:text-surgical-blue-600'
                    }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* User Menu / Auth Buttons */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center space-x-2 rounded-md px-3 py-2 text-sm font-medium text-surgical-gray-700 hover:bg-surgical-gray-50"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-surgical-blue-100 text-surgical-blue-600">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <span className="hidden md:inline">{user.name}</span>
                  <svg
                    className={`h-4 w-4 transition-transform ${isUserMenuOpen ? 'rotate-180' : ''
                      }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>

                {/* User Dropdown Menu */}
                {isUserMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setIsUserMenuOpen(false)}
                    />
                    <div className="absolute right-0 z-20 mt-2 w-48 rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5">
                      <Link
                        href="/profile"
                        className="block px-4 py-2 text-sm text-surgical-gray-700 hover:bg-surgical-gray-50"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        Profile
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="block w-full px-4 py-2 text-left text-sm text-surgical-gray-700 hover:bg-surgical-gray-50"
                      >
                        Logout
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="hidden md:flex md:items-center md:space-x-2">
                <Link
                  href="/login"
                  className="rounded-md px-4 py-2 text-sm font-medium text-surgical-gray-700 hover:bg-surgical-gray-50"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="rounded-md bg-surgical-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-surgical-blue-700"
                >
                  Sign Up
                </Link>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden rounded-md p-2 text-surgical-gray-700 hover:bg-surgical-gray-50"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {isMobileMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-surgical-gray-200 py-2">
            {visibleNavLinks.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`block rounded-md px-3 py-2 text-base font-medium ${isActive
                      ? 'bg-surgical-blue-50 text-surgical-blue-600'
                      : 'text-surgical-gray-700 hover:bg-surgical-gray-50'
                    }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              );
            })}
            {!isAuthenticated && (
              <div className="mt-2 space-y-2 border-t border-surgical-gray-200 pt-2">
                <Link
                  href="/login"
                  className="block rounded-md px-3 py-2 text-base font-medium text-surgical-gray-700 hover:bg-surgical-gray-50"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="block rounded-md bg-surgical-blue-600 px-3 py-2 text-base font-medium text-white hover:bg-surgical-blue-700"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        )}
      </nav>
    </header>
  );
}
