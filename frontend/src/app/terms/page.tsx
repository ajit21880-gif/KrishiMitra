"use client";

import React from "react";
import Link from "next/link";
import { ArrowLeft, ShieldAlert, FileText, Mail, Info } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 flex flex-col">
      {/* Header */}
      <header className="bg-primary-600 text-white p-4 shadow flex items-center gap-3">
        <Link 
          href="/" 
          className="p-1 rounded-full hover:bg-primary-700 transition flex items-center justify-center text-white"
          aria-label="Back to Dashboard"
        >
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="font-extrabold text-lg tracking-tight">Terms & Conditions</h1>
          <p className="text-xs text-green-100">Disclaimers, Data Ownership & Limitation of Liability</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-4 max-w-2xl mx-auto w-full space-y-6 py-6">
        {/* Important Notice */}
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 text-xs text-amber-950 space-y-2">
          <div className="flex items-center gap-2 font-bold text-amber-900">
            <ShieldAlert size={18} />
            <h2 className="text-sm">Data Ownership & Public Source Disclaimer</h2>
          </div>
          <p className="leading-relaxed">
            <strong>CrestSubarn does not own, generate, or independently alter any agricultural commodity price records or market data displayed in KrishiMitra AI.</strong> All market prices, daily arrivals, modal figures, and variety details are sourced directly from public government websites and APIs, including <strong>data.gov.in</strong>, <strong>AGMARKNET</strong>, <strong>e-NAM</strong>, and <strong>UPAg</strong>.
          </p>
        </div>

        {/* Detailed Terms */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-5 text-xs text-gray-700 leading-relaxed">
          <div className="space-y-1.5">
            <h3 className="font-bold text-sm text-gray-900 flex items-center gap-2">
              <FileText className="text-primary-600" size={16} />
              1. Unified Information Platform
            </h3>
            <p>
              The sole purpose of KrishiMitra AI is to provide Indian farmers with a consolidated, user-friendly, and multilingual overview of public government datasets. It is built as a non-profit, free public utility to simplify access to mandi trends and agricultural advice.
            </p>
          </div>

          <div className="space-y-1.5 border-t border-gray-100 pt-4">
            <h3 className="font-bold text-sm text-gray-900 flex items-center gap-2">
              <Info className="text-primary-600" size={16} />
              2. Limitation of Liability
            </h3>
            <p>
              Because data is retrieved in real-time or via scheduled synchronization from government portals, discrepancies, typographical errors, transmission lags, or omissions present in source government records may reflect in the application.
            </p>
            <p className="font-medium text-gray-800">
              CrestSubarn and its team shall not be held liable for any financial losses, trading outcomes, transportation expenses, or harvest sales decisions made on the basis of displayed figures. Farmers and traders are advised to verify prices at the respective local APMC yard before completing high-value transactions.
            </p>
          </div>

          <div className="space-y-1.5 border-t border-gray-100 pt-4">
            <h3 className="font-bold text-sm text-gray-900 flex items-center gap-2">
              <ShieldAlert className="text-primary-600" size={16} />
              3. Marketplace & Dealer Listings
            </h3>
            <p>
              Dealers, input inventories, and wholesaler contacts listed in the marketplace tab are cataloged for farmer convenience. CrestSubarn does not endorse or warranty third-party products, fertilizers, seeds, or trade settlements between buyers and sellers.
            </p>
          </div>

          <div className="space-y-1.5 border-t border-gray-100 pt-4">
            <h3 className="font-bold text-sm text-gray-900 flex items-center gap-2">
              <Mail className="text-primary-600" size={16} />
              4. Support & Contact
            </h3>
            <p>
              If you discover an error, have questions regarding mandi mappings, or wish to submit feedback, please contact our support desk:
            </p>
            <p className="font-mono font-bold text-primary-600 text-sm mt-1">
              <a href="mailto:support@crestsubarn.com" className="hover:underline">
                support@crestsubarn.com
              </a>
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="flex justify-between items-center text-xs text-primary-700 font-bold px-2">
          <Link href="/about" className="hover:underline">
            ← About CrestSubarn
          </Link>
          <Link href="/acknowledgements" className="hover:underline">
            Government Acknowledgements →
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-100 text-[10px] text-gray-500 text-center py-3 border-t border-gray-200">
        © 2026 Crestsubarn. All rights reserved.
      </footer>
    </div>
  );
}
