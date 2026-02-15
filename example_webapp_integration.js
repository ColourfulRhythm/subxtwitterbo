/**
 * Example: How to integrate Twitter API with your webapp
 * 
 * This shows how to call the API when a user makes a purchase
 */

// Configuration
const TWITTER_API_URL = 'http://localhost:5001/api/post-tweet'; // Change to your API URL
const API_SECRET_KEY = 'your_secret_key_here'; // Get from .env file

/**
 * Example: Post tweet when user completes a purchase
 */
async function handlePurchaseComplete(purchaseData) {
    try {
        // Call your Twitter API
        const response = await fetch(TWITTER_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_SECRET_KEY
            },
            body: JSON.stringify({
                purchase: {
                    user_name: purchaseData.customerName || 'A customer',
                    product: purchaseData.productName,
                    amount: formatCurrency(purchaseData.amount, purchaseData.currency),
                    location: purchaseData.location || ''
                },
                custom_message: '🎉'
            })
        });

        const result = await response.json();

        if (result.success) {
            console.log('✅ Tweet posted:', result.tweet_url);
            // Optionally show success message to user
            showNotification('Purchase shared on Twitter! 🎉');
        } else {
            console.error('❌ Failed to post tweet:', result.error);
            // Don't fail the purchase, just log the error
        }
    } catch (error) {
        console.error('❌ Error calling Twitter API:', error);
        // Don't fail the purchase if Twitter API fails
    }
}

/**
 * Example: Post custom tweet
 */
async function postCustomTweet(tweetText) {
    try {
        const response = await fetch(TWITTER_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_SECRET_KEY
            },
            body: JSON.stringify({
                tweet: tweetText
            })
        });

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('❌ Error posting tweet:', error);
        throw error;
    }
}

/**
 * Helper: Format currency
 */
function formatCurrency(amount, currency = 'NGN') {
    if (currency === 'NGN') {
        return `₦${parseFloat(amount).toLocaleString()}`;
    }
    return `${currency} ${parseFloat(amount).toLocaleString()}`;
}

/**
 * Example: Integration with payment processor webhook
 */
// If using Stripe, PayPal, etc., you can call this from your webhook handler
async function handlePaymentWebhook(webhookData) {
    // Extract purchase information from webhook
    const purchaseData = {
        customerName: webhookData.customer?.name || webhookData.customer_email,
        productName: webhookData.product_name || webhookData.description,
        amount: webhookData.amount || webhookData.total,
        currency: webhookData.currency || 'NGN',
        location: webhookData.shipping_address?.city || ''
    };

    // Post to Twitter
    await handlePurchaseComplete(purchaseData);
}

// Example usage in your purchase flow:
/*
document.getElementById('checkout-button').addEventListener('click', async () => {
    // ... your purchase logic ...
    
    // After successful purchase
    const purchaseData = {
        customerName: 'John Doe',
        productName: 'Land at 2 Seasons',
        amount: 500000,
        currency: 'NGN',
        location: 'Abeokuta'
    };
    
    // Post to Twitter (don't await - let it run in background)
    handlePurchaseComplete(purchaseData).catch(console.error);
});
*/

