import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe('pk_test_51QwvrgPJwVMQsXXob37groN7u8Bv4y1EkwIQf7geeFV6ql3tUwPXuWEdTX7DZdh98dFwSMTc6AkhN7GomoiYkXu600mq4nr0eJ');

function PaymentForm() {
    const stripe = useStripe();
    const elements = useElements();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!stripe || !elements) return;
        const payload = await stripe.confirmCardPayment('pi_client_secret', {
            payment_method: {
                card: elements.getElement(CardElement)!,
            },
        });

        if (payload.error) {
            console.error('Ошибка платежа:', payload.error.message);
        } else {
            alert('Платеж успешно выполнен!');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <CardElement />
            <button type="submit" disabled={!stripe}>
                Оплатить
            </button>
        </form>
    );
}

export default function Checkout() {
    return (
        <Elements stripe={stripePromise}>
            <PaymentForm />
        </Elements>
    );
}