import React from 'react';
import { Link } from 'react-router-dom';
import './styles/HomePage.css';

const HomePage: React.FC = () => (
    <div className="HomePage">
        <div className="panel">
            <p>Helps to create a structure for warehouse and accounting codes, mainly for fasteners - screws, nuts,
                washers for the accounting program for a manufacturing company - to initially insert them into the accounting
                program database. This ensures consistent naming as the database evolves and different names are used across a wide
                range of products.</p>
        </div>
        <div className="buttons">
            <div className="Button1">s
                <Link to="/main-page">
                    <button>Get Started!</button>
                </Link>
            </div>
            <div className="Button2">
                <Link to="/main-test">
                    <button>Test Page</button>
                </Link>
            </div>
        </div>
    </div>
);

export default HomePage;