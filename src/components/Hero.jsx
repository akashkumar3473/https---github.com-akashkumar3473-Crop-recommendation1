import React from 'react';
import WeatherDisplay from './WeatherDisplay'; // Naya component import karein

const Hero = ({ setPage, currentPage, onLogout, userName, language, setLanguage, title, subtitle, heroImage, weather, t }) => {
    // Nav links
    const navLinks = [
        { name: t.dashboard, page: 'dashboard' },
        { name: t.notifications, page: 'notifications' },
        { name: t.ourTeam, page: 'team' }
    ];

    return (
        <header className="relative bg-cover bg-center text-white p-6 md:p-8 rounded-b-3xl shadow-2xl overflow-hidden mb-8" style={{backgroundImage: `url(${heroImage})`}}>
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/40 to-transparent"></div>
            
            <div className="relative z-10">
                {/* Top Bar: Weather, User Info, Logout */}
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center space-x-4">
                        <select value={language} onChange={(e) => setLanguage(e.target.value)} className="bg-white/20 backdrop-blur-sm text-white rounded-md p-2 text-sm focus:outline-none">
                            <option value="en" className="text-black">English</option>
                            <option value="hi" className="text-black">हिन्दी</option>
                        </select>
                        {/* --- ADDED: WeatherDisplay Component --- */}
                        <div className="hidden sm:block">
                             <WeatherDisplay weather={weather} t={t} />
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        <span className="font-semibold hidden md:inline">{t.welcome}, {userName}</span>
                        <button onClick={onLogout} className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-300">
                            {t.logout}
                        </button>
                    </div>
                </div>

                {/* Main Hero Content */}
                <div className="text-center py-10">
                    <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-3" style={{textShadow: '2px 2px 8px rgba(0,0,0,0.7)'}}>{title}</h1>
                    <p className="text-lg md:text-xl max-w-3xl mx-auto text-gray-200" style={{textShadow: '1px 1px 4px rgba(0,0,0,0.7)'}}>{subtitle}</p>
                </div>
                
                {/* Navigation Tabs */}
                <nav className="flex justify-center space-x-2 md:space-x-4 bg-black/30 backdrop-blur-sm p-2 rounded-xl max-w-md mx-auto">
                    {navLinks.map(link => (
                        <button 
                            key={link.page} 
                            onClick={() => setPage(link.page)}
                            className={`px-4 py-2 text-sm md:text-base font-semibold rounded-lg transition-all duration-300 w-full ${currentPage === link.page ? 'bg-white text-green-700 shadow-md' : 'text-white hover:bg-white/20'}`}
                        >
                            {link.name}
                        </button>
                    ))}
                </nav>
            </div>
        </header>
    );
};

export default Hero;
