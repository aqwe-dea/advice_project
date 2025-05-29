import React, { useState } from 'react';
import axios from 'axios';
import {loadStripe} from '@stripe/stripe-js';
import {Stripe} from '@stripe/stripe-js'; 

const stripePublicKey = process.env.REACT_APP_STRIPE_PUBLIC_KEY;
if (!stripePublicKey) {
    console.error('Не найден REACT_APP_STRIPE_PUBLIC_KEY');
}

const stripePromise = loadStripe(stripePublicKey as string);

interface DonationFormData {
    amount: number;
}

function StripeDonation({ onSuccess }: { onSuccess?: () => void }) {
    const [amount, setAmount] = useState<number>(500);
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!stripePublicKey) {
            alert('Stripe ключ не настроен!');
            return;
        }
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/create-checkout-session/ ',
                { amount, currency: 'usd' },
                { headers: { 'Content-Type': 'application/json' } }
            );
            const stripe = await stripePromise;
            if (!stripe) {
                alert('Не удалось загрузить Stripe.');
                return;
            }
            const { error } = await stripe.redirectToCheckout({
                sessionId: response.data.sessionId,
            })
            if (error) {
                console.error('Ошибка при перенаправлении на Stripe:', error.message);
                alert('Протзошла ошибка при оплате.');
            } else {
                alert('Перенаправлениее на оплату...');
                onSuccess?.();
            }
        } catch (error: any) {
            console.error('Ошибка создании сессии:', error);
            alert('Не удалось создать сессию оплаты.');
        }
    };
    return (
        <div className="donation-form">
            <h2>Поддержите проект Советница АКВИ</h2>
            <p>Выберите сумму пожертвования:</p>
            <form onSubmit={handleSubmit}>
                <input
                 type="number"
                 placeholder="Сумма ($)"
                 value={amount / 100}
                 onChange={(e) => setAmount(parseFloat(e.target.value) * 100)}
                />
                <button type="submit">Оплатить</button>
            </form>
        </div>
    );
}
export default StripeDonation;