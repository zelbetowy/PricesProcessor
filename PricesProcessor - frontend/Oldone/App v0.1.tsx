
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'; 
import './styles/App.css';
import './styles/home-page.css';
import './styles/main-page.css';

import Navbar from '../src/Navbar'; 
import './styles/Navbar.css';


function App() {
    return (
        <Router>
            <div>

                <Navbar /> {/* Belka nawigacyjna */}
                <div style={{ marginTop: '20px' }}> {/* Dodajemy odstêp, aby treœæ nie zas³ania³a belki */}


                    <Routes>
                        <Route path="/" element={
                            <div className="home-page">
                                <div className="panel">
                                <p>App helps to create a structure for warehouse and accounting codes, mainly for fasteners - screws, nuts,
                                    washers for the accounting program for a manufacturing company - to initially insert them into the accounting
                                    program database. This ensures consistent naming as the database evolves and different names are used across a wide
                                        range of products.</p>
                                </div>

                                <div className="Button1">
                                    <Link to="/main-page">
                                        <button>Get Started!</button>
                                    </Link>
                                </div>

                            </div>
                        } />

                        <Route path="/main-page" element={
                            <div className="main-page">
                                <h1>Page 2</h1>
                                <p>This is another page</p>

                                <div className="Button2">
                                    <Link to="/home-page">
                                        <button>Get Started!</button>
                                    </Link>
                            
                                </div>
                            </div>
                        } />
                    </Routes>

                </div>
            </div>

        </Router>
    );
}

export default App;

