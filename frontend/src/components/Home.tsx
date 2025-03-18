import React from 'react';
import AdviceForm from './AdviceForm';
import AdviceList from './AdviceList';

function Home() {
    return (
        <div className="home-page">
            <h1>Советница АКВИ</h1>
            <AdviceForm />
            <AdviceList />
            </div>
    );
}

export default Home;