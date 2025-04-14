import React, { useState } from 'react';
import axios from 'axios';
import { loadStripe } from '@stripe/stripe-js';
import { RedirectToCheckoutOptions } from '@stripe/stripe-js';

const stripePublicKey = process.env.REACT_APP_STRIPE_PUBLIC_KEY;
const stripePromise = loadStripe(stripePublicKey as string);
if (!stripePublicKey) {
    console.error('Не найден REACT_APP_STRIPE_PUBLIC_KEY');
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
            const stripe = await stripePromise;
            const response = await axios.post(
                'https://advice-project.onrender.com/create-payment-intent/',
                { amount, currency: 'usd' }
            );
            const { error } = await stripe!.RedirectToCheckout({
                paymentIntentClientSecret: response.data.clientSecret
            });
            if (error) {
                console.error('Ошибка при перенаправлении на Stripe:', error);
                alert('Произошла ошибка при оплате.');
            } else {
                alert('Пожертвование успешно!');
                onSuccess?.();
            }
        } catch (error) {
            console.error('Ошибка при создании платежа:', error);
            alert('Произошла ошибка при создании платежа.');
        }
    };
    return (
        <div className="donation-form">
            <h2>Поддержите проект "Советница АКВИ"</h2>
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