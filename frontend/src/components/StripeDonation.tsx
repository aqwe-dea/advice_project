import React, { useState } from 'react';
import axios from 'axios';
import {loadStripe} from '@stripe/stripe-js';
import {RedirectToCheckoutOptions} from '@stripe/stripe-js';
import {RedirectToCheckoutClientOptions} from '@stripe/stripe-js';
import {StripeElementsOptionsClientSecret} from '@stripe/stripe-js';
import {StripeCheckoutOptions} from '@stripe/stripe-js';
import {Stripe} from '@stripe/stripe-js'; 

interface DonationFormData {
    amount: number;
}
function StripeDonation({ onSuccess }: { onSuccess?: () => void }) {
    const stripePublicKey = process.env.REACT_APP_STRIPE_PUBLIC_KEY;
        if (!stripePublicKey) {
            console.error('Не найден REACT_APP_STRIPE_PUBLIC_KEY');
        }
    const stripePromise = loadStripe(stripePublicKey as string);
    const [amount, setAmount] = useState<number>(500);
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!stripePublicKey) {
            alert('Stripe ключ не настроен!');
            return;
        }
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/create-payment-intent/ ',
                { amount, currency: 'usd' },
                { headers: { 'Content-Type': 'application/json' } }
            );
            const { sessionId } = response.data;
            const stripe = await stripePromise;
            if (!stripe) {
                alert('Не удалось загрузить Stripe.');
                return;
            }
            const checkoutOptions: RedirectToCheckoutOptions = {
                 ClientSecret: response.data.clientSecret, 
            };
            const { url } = await stripe.redirectToCheckout({ sessionId: response.data.sessionId });
            if (url) {
                window.location.href = url;
                console.error('Ошибка при перенаправлении на Stripe:', error);
                alert('Протзошла ошибка при оплате.');
            } else {
                alert('Пожертвование успешно!');
                onSuccess?.();
            }
        } catch (error: any) {
            console.error('Ошибка при создании платежа:', error);
            alert('Произошла ошибка при создании платежа.');
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