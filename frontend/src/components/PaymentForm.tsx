import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY || '');
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