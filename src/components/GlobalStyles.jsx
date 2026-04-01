const GlobalStyles = () => (
    <style>{`
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
            animation: fadeIn 0.6s ease-out forwards;
            opacity: 0;
        }
        @keyframes fadeInStagger {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .animate-fadeInStagger {
            animation: fadeInStagger 0.5s ease-out forwards;
            opacity: 0; 
        }
        @keyframes wave {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        .water-animation {
            content: "";
            position: absolute;
            left: 0;
            width: 200%;
            height: 100%;
            background-repeat: repeat no-repeat;
            background-position: 0 bottom;
            transform-origin: center bottom;
            animation: wave 3s linear infinite;
        }
    `}</style>
);

export default GlobalStyles;