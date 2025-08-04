'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  CheckCircleIcon,
  CreditCardIcon,
  UserGroupIcon,
  StarIcon,
  HeartIcon
} from '@heroicons/react/24/outline';

interface DonationTier {
  id: string;
  name: string;
  amount: number;
  monthly: boolean;
  description: string;
  features: string[];
  popular?: boolean;
  badge?: string;
}

const donationTiers: DonationTier[] = [
  {
    id: 'supporter',
    name: 'Democracy Supporter',
    amount: 10,
    monthly: true,
    description: 'Help keep the platform running and accessible',
    features: [
      'Support server costs and daily data updates',
      'Quarterly transparency reports',
      'Community recognition',
      'Platform sustainability funding'
    ]
  },
  {
    id: 'champion',
    name: 'Civic Champion',
    amount: 25,
    monthly: true,
    description: 'Power AI processing and advanced features',
    popular: true,
    features: [
      'Everything in Democracy Supporter',
      'Fund AI processing for 100+ bill summaries',
      'Priority feature suggestions via email',
      'Early notification of major legislation',
      'Monthly platform usage statistics'
    ]
  },
  {
    id: 'advocate',
    name: 'Transparency Advocate',
    amount: 50,
    monthly: true,
    description: 'Enable advanced civic engagement tools',
    badge: 'Maximum Impact',
    features: [
      'Everything in Civic Champion',
      'Support advanced search development',
      'Direct input on feature roadmap',
      'Quarterly video calls with development team',
      'Recognition as platform founding supporter'
    ]
  }
];

const oneTimeAmounts = [25, 50, 100, 250];

export function DonationForm() {
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [donationType, setDonationType] = useState<'monthly' | 'oneTime'>('monthly');
  const [customAmount, setCustomAmount] = useState<string>('');
  const [selectedOneTime, setSelectedOneTime] = useState<number | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleDonationSelect = (tierId: string) => {
    setSelectedTier(tierId);
    setDonationType('monthly');
    setSelectedOneTime(null);
    setCustomAmount('');
  };

  const handleOneTimeSelect = (amount: number) => {
    setSelectedOneTime(amount);
    setDonationType('oneTime');
    setSelectedTier(null);
    setCustomAmount('');
  };

  const handleCustomAmount = (amount: string) => {
    setCustomAmount(amount);
    setDonationType('oneTime');
    setSelectedTier(null);
    setSelectedOneTime(null);
  };

  const handleDonate = async () => {
    setIsProcessing(true);
    
    // In a real implementation, this would integrate with Stripe, PayPal, or another payment processor
    let amount: number;
    let isMonthly: boolean;
    
    if (selectedTier) {
      const tier = donationTiers.find(t => t.id === selectedTier);
      amount = tier?.amount || 0;
      isMonthly = true;
    } else if (selectedOneTime) {
      amount = selectedOneTime;
      isMonthly = false;
    } else if (customAmount) {
      amount = parseFloat(customAmount);
      isMonthly = false;
    } else {
      setIsProcessing(false);
      return;
    }

    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Here you would normally:
      // 1. Create a Stripe Checkout session or PayPal payment
      // 2. Redirect to payment processor
      // 3. Handle webhooks for payment confirmation
      // 4. Update user's supporter status in database
      // 5. Send confirmation email
      
      alert(`Thank you for your ${isMonthly ? 'monthly' : 'one-time'} donation of $${amount}! Payment processing would normally redirect you to Stripe/PayPal.`);
      
    } catch (error) {
      alert('Payment processing failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const getSelectedAmount = () => {
    if (selectedTier) {
      const tier = donationTiers.find(t => t.id === selectedTier);
      return tier?.amount || 0;
    }
    if (selectedOneTime) return selectedOneTime;
    if (customAmount) return parseFloat(customAmount) || 0;
    return 0;
  };

  const hasSelection = selectedTier || selectedOneTime || (customAmount && parseFloat(customAmount) > 0);

  return (
    <div className="space-y-8">
      {/* Donation Type Toggle */}
      <div className="flex justify-center">
        <div className="bg-gray-100 p-1 rounded-lg flex">
          <button
            onClick={() => setDonationType('monthly')}
            className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
              donationType === 'monthly'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Monthly Support
          </button>
          <button
            onClick={() => setDonationType('oneTime')}
            className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
              donationType === 'oneTime'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            One-Time Gift
          </button>
        </div>
      </div>

      {/* Monthly Donation Tiers */}
      {donationType === 'monthly' && (
        <div className="grid md:grid-cols-3 gap-6">
          {donationTiers.map((tier) => (
            <Card 
              key={tier.id}
              className={`relative cursor-pointer transition-all duration-200 ${
                selectedTier === tier.id
                  ? 'ring-2 ring-blue-500 border-blue-200 shadow-lg'
                  : 'hover:shadow-md border-gray-200'
              } ${tier.popular ? 'border-green-300 bg-green-50' : ''}`}
              onClick={() => handleDonationSelect(tier.id)}
            >
              {tier.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-green-600 text-white px-3 py-1">Most Popular</Badge>
                </div>
              )}
              {tier.badge && (
                <div className="absolute -top-3 right-4">
                  <Badge className="bg-purple-600 text-white px-3 py-1">{tier.badge}</Badge>
                </div>
              )}
              
              <CardHeader>
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-900">{tier.name}</h3>
                  <div className="mt-2">
                    <span className="text-3xl font-bold text-gray-900">${tier.amount}</span>
                    <span className="text-gray-600">/month</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">{tier.description}</p>
                </div>
              </CardHeader>
              
              <CardContent>
                <ul className="space-y-2 mb-6">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                      <CheckCircleIcon className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* One-Time Donations */}
      {donationType === 'oneTime' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {oneTimeAmounts.map((amount) => (
              <button
                key={amount}
                onClick={() => handleOneTimeSelect(amount)}
                className={`p-4 border rounded-lg text-center transition-all duration-200 ${
                  selectedOneTime === amount
                    ? 'border-blue-500 bg-blue-50 text-blue-700 font-semibold'
                    : 'border-gray-300 hover:border-gray-400 text-gray-700'
                }`}
              >
                ${amount}
              </button>
            ))}
          </div>
          
          <div className="max-w-md mx-auto">
            <label htmlFor="custom-amount" className="block text-sm font-medium text-gray-700 mb-2">
              Or enter a custom amount:
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
              <input
                id="custom-amount"
                type="number"
                min="1"
                step="1"
                value={customAmount}
                onChange={(e) => handleCustomAmount(e.target.value)}
                className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="25"
              />
            </div>
          </div>
        </div>
      )}

      {/* Donation Summary and Action */}
      {hasSelection && (
        <Card className="max-w-md mx-auto border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="flex items-center justify-center mb-4">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                  <HeartIcon className="h-5 w-5 text-white" />
                </div>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {donationType === 'monthly' ? 'Monthly Support' : 'One-Time Donation'}
              </h3>
              
              <div className="text-2xl font-bold text-blue-600 mb-2">
                ${getSelectedAmount()}{donationType === 'monthly' ? '/month' : ''}
              </div>
              
              {selectedTier && (
                <p className="text-sm text-gray-600 mb-4">
                  {donationTiers.find(t => t.id === selectedTier)?.name}
                </p>
              )}
              
              <Button
                onClick={handleDonate}
                disabled={isProcessing}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 text-base"
              >
                {isProcessing ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Processing...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <CreditCardIcon className="h-5 w-5" />
                    Donate {donationType === 'monthly' ? 'Monthly' : 'Now'}
                  </div>
                )}
              </Button>
              
              <p className="text-xs text-gray-600 mt-3">
                Secure payment processing via Stripe. Cancel anytime.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Payment Security Notice */}
      <div className="max-w-2xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full text-sm text-gray-600">
          <CheckCircleIcon className="h-4 w-4 text-green-600" />
          <span>Secure • Tax-deductible • Cancel anytime</span>
        </div>
      </div>
    </div>
  );
}