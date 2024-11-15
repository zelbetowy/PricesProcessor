import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';  // Import nowego komponentu HomePage
import MainPageConst from './MainPage';  // Import nowego komponentu MainPage
import MainTestConst from './MainTest';  // Import nowego komponentu MainTest
import Navbar from './Navbar';
import './styles/App.css';
import './styles/Navbar.css';

const App: React.FC = () => {
    return (
        <Router>
            <div>
                <Navbar />
                <div style={{ marginTop: '80px' }}>
                    <Routes>
                        <Route path="/" element={<HomePage />} /> {/* U¿ywamy nowego komponentu HomePage */}
                        <Route path="/main-page" element={<MainPageConst />} /> {/* U¿ywamy nowego komponentu MainPage */}
                        <Route path="/main-test" element={<MainTestConst />} /> {/* U¿ywamy nowego komponentu MainTest */}
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

export default App;