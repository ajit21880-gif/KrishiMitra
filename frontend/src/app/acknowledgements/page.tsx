"use client";

import React from "react";
import Link from "next/link";
import { ArrowLeft, Landmark, Award, ExternalLink, HeartHandshake } from "lucide-react";

export default function AcknowledgementsPage() {
  const initiatives = [
    {
      agency: "Digital India Bhashini (NLTM, MeitY)",
      title: "National Language Translation Mission",
      description: "Provides state-of-the-art neural speech recognition (ASR), translation (NMT), and high-fidelity text-to-speech (TTS) across 13 Indian languages (Hindi, Kannada, Gujarati, Marathi, Tamil, Telugu, Malayalam, Punjabi, Bengali, Odia, Assamese, Kashmiri, and English). This allows KrishiMitra to offer natural, spoken voice interactions to farmers in their mother tongue.",
      portalUrl: "https://bhashini.gov.in"
    },
    {
      agency: "data.gov.in / AGMARKNET",
      title: "Open Government Data Platform & Ministry of Agriculture",
      description: "Provides daily wholesale arrival and price feeds across thousands of agricultural produce market committees (APMCs) throughout India. This public API enables KrishiMitra to provide accurate, daily-synced modal, minimum, and maximum mandi rates.",
      portalUrl: "https://data.gov.in"
    },
    {
      agency: "e-NAM (National Agriculture Market)",
      title: "Small Farmers' Agribusiness Consortium (SFAC)",
      description: "Connects APMC mandis into a unified electronic trading network. KrishiMitra leverages e-NAM data to present trade depth, commodity varieties, quality grades, and electronic auction transparency directly to farmers.",
      portalUrl: "https://enam.gov.in"
    },
    {
      agency: "UPAg & Dept of Consumer Affairs (DoCA)",
      title: "Unified Portal for Agricultural Statistics",
      description: "Furnishes essential macroeconomic indicators, retail price spreads, reservoir storage levels, and CWWG rainfall departure statistics, giving farmers actionable guidance on whether to hold or sell their produce.",
      portalUrl: "https://upag.gov.in"
    }
  ];

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
          <h1 className="font-extrabold text-lg tracking-tight">Government Acknowledgements</h1>
          <p className="text-xs text-green-100">Gratitude to National Public Data Initiatives</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-4 max-w-2xl mx-auto w-full space-y-6 py-6">
        {/* Gratitude Statement */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-3">
          <div className="flex items-center gap-2 text-primary-700 font-bold">
            <HeartHandshake size={24} />
            <h2 className="text-lg">Our Sincere Thanks</h2>
          </div>
          <p className="text-xs text-gray-700 leading-relaxed">
            KrishiMitra AI is made possible through the progressive, open-access digital infrastructure established by the 
            <strong> Government of India</strong>. We extend our deepest gratitude to the ministries, departments, and technical teams whose 
            freely provided public APIs, language models, and agricultural datasets allow this platform to operate 
            <strong> completely free of charge for Indian farmers</strong>.
          </p>
        </div>

        {/* Initiatives List */}
        <div className="space-y-4">
          {initiatives.map((item, idx) => (
            <div key={idx} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 space-y-2">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2">
                  <Landmark className="text-primary-600 shrink-0" size={18} />
                  <h3 className="font-bold text-sm text-gray-900">{item.agency}</h3>
                </div>
                <a 
                  href={item.portalUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-[11px] text-primary-600 hover:underline flex items-center gap-1 font-semibold"
                >
                  Visit Portal <ExternalLink size={12} />
                </a>
              </div>
              <p className="text-xs font-semibold text-gray-600">{item.title}</p>
              <p className="text-xs text-gray-600 leading-relaxed">{item.description}</p>
            </div>
          ))}
        </div>

        {/* Special Acknowledgement to MeitY */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-5 text-xs text-blue-950 space-y-2">
          <div className="flex items-center gap-2 font-bold text-blue-900">
            <Award size={18} />
            <h4>Empowering Rural Inclusivity through Digital India Bhashini</h4>
          </div>
          <p className="leading-relaxed text-[11px] text-blue-900">
            Special recognition to the <strong>Ministry of Electronics and Information Technology (MeitY)</strong> and the 
            <strong> Digital India Bhashini Division</strong> for championing open, indigenous AI models that bridge linguistic divides, 
            ensuring that technology serves every farmer in every corner of India in their own language.
          </p>
        </div>

        {/* Navigation Links */}
        <div className="flex justify-between items-center text-xs text-primary-700 font-bold px-2">
          <Link href="/about" className="hover:underline">
            ← About CrestSubarn
          </Link>
          <Link href="/terms" className="hover:underline">
            Terms & Conditions →
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
