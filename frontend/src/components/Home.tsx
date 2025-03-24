import React from 'react';
import AdviceForm from './AdviceForm';
import AdviceList from './AdviceList';

function Home({ onSuccess }: { onSuccess?: () => void }) {
    return (
        <div className="home-page">
            <h1>Советница АКВИ</h1>
            <AdviceForm onSuccess={onSuccess} />
            <AdviceList />
            </div>
    );
}

export default Home;