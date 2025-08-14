import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  FiUser, 
  FiCreditCard, 
  FiDollarSign, 
  FiSend, 
  FiAlertCircle,
  FiCheckCircle
} from 'react-icons/fi';
import { toast } from 'react-hot-toast';
import { Helmet } from 'react-helmet-async';

import { useAuth } from '../hooks/useAuth';
import apiService from '../services/api';
import { Account, TransferPriority, TransferType } from '../types';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';

interface TransferFormData {
  source_account_id: string;
  beneficiary_name: string;
  beneficiary_iban: string;
  beneficiary_bic: string;
  amount: number;
  currency: string;
  description: string;
  priority: TransferPriority;
  transfer_type: TransferType;
}

const schema = yup.object({
  source_account_id: yup.string().required('Source account is required'),
  beneficiary_name: yup.string().required('Beneficiary name is required').min(2, 'Name must be at least 2 characters'),
  beneficiary_iban: yup.string().required('IBAN is required').min(15, 'IBAN must be at least 15 characters'),
  beneficiary_bic: yup.string().required('BIC is required').min(8, 'BIC must be at least 8 characters'),
  amount: yup.number().required('Amount is required').positive('Amount must be positive'),
  currency: yup.string().required('Currency is required'),
  description: yup.string().required('Description is required').min(5, 'Description must be at least 5 characters'),
  priority: yup.string().required('Priority is required'),
  transfer_type: yup.string().required('Transfer type is required')
}).required();

const TransferForm: React.FC = () => {
  const [ibanValidating, setIbanValidating] = useState(false);
  const [ibanValid, setIbanValid] = useState<boolean | null>(null);
  const [bankInfo, setBankInfo] = useState<any>(null);
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Fetch user accounts
  const { data: accounts, isLoading: accountsLoading } = useQuery<Account[]>(
    'user-accounts',
    () => apiService.getAccounts().then(res => res.items),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Fetch supported currencies
  const { data: currencies, isLoading: currenciesLoading } = useQuery<string[]>(
    'currencies',
    apiService.getSupportedCurrencies,
    {
      staleTime: 60 * 60 * 1000, // 1 hour
    }
  );

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    setValue,
    trigger
  } = useForm<TransferFormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      priority: TransferPriority.NORMAL,
      transfer_type: TransferType.SWIFT,
      currency: 'USD'
    }
  });

  // Watch form values for real-time validation
  const watchedIban = watch('beneficiary_iban');
  const watchedAmount = watch('amount');
  const watchedSourceAccount = watch('source_account_id');

  // IBAN validation mutation
  const validateIbanMutation = useMutation(
    (iban: string) => apiService.validateIBAN(iban),
    {
      onSuccess: (data) => {
        setIbanValid(data.valid);
        setBankInfo(data.bank_info);
        if (data.valid) {
          toast.success('IBAN validated successfully');
        } else {
          toast.error('Invalid IBAN');
        }
      },
      onError: () => {
        setIbanValid(false);
        setBankInfo(null);
        toast.error('Failed to validate IBAN');
      },
      onSettled: () => {
        setIbanValidating(false);
      }
    }
  );

  // Create transfer mutation
  const createTransferMutation = useMutation(
    (data: TransferFormData) => apiService.createTransfer(data),
    {
      onSuccess: (transfer) => {
        toast.success('Transfer created successfully!');
        queryClient.invalidateQueries('transfers');
        queryClient.invalidateQueries('dashboard-stats');
        navigate(`/transfer/${transfer.id}`);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create transfer');
      }
    }
  );

  // Validate IBAN on change
  React.useEffect(() => {
    if (watchedIban && watchedIban.length >= 15) {
      const timeoutId = setTimeout(() => {
        setIbanValidating(true);
        validateIbanMutation.mutate(watchedIban);
      }, 1000);

      return () => clearTimeout(timeoutId);
    } else {
      setIbanValid(null);
      setBankInfo(null);
    }
  }, [watchedIban]);

  const onSubmit = async (data: TransferFormData) => {
    if (!ibanValid) {
      toast.error('Please enter a valid IBAN');
      return;
    }

    createTransferMutation.mutate(data);
  };

  const getSelectedAccount = () => {
    return accounts?.find(acc => acc.id === watchedSourceAccount);
  };

  const selectedAccount = getSelectedAccount();

  if (accountsLoading || currenciesLoading) {
    return <LoadingSpinner text="Loading transfer form..." />;
  }

  return (
    <>
      <Helmet>
        <title>New Transfer - Banking Transfer Platform</title>
      </Helmet>

      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              New Transfer
            </h1>
            <p className="text-gray-600">
              Create a new bank transfer to any account worldwide
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Source Account */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source Account
              </label>
              <select
                {...register('source_account_id')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select an account</option>
                {accounts?.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_number} - {account.currency} (${account.balance.toLocaleString()})
                  </option>
                ))}
              </select>
              {errors.source_account_id && (
                <p className="mt-1 text-sm text-red-600">{errors.source_account_id.message}</p>
              )}
            </div>

            {/* Account Balance Info */}
            {selectedAccount && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="bg-blue-50 p-4 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-blue-700">
                    Available Balance: ${selectedAccount.balance.toLocaleString()}
                  </span>
                  <span className="text-sm text-blue-700">
                    Daily Limit: ${selectedAccount.daily_limit.toLocaleString()}
                  </span>
                </div>
              </motion.div>
            )}

            {/* Beneficiary Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Beneficiary Name"
                placeholder="Enter beneficiary name"
                icon={<FiUser className="w-5 h-5" />}
                {...register('beneficiary_name')}
                error={errors.beneficiary_name?.message}
              />

              <Input
                label="Currency"
                placeholder="Select currency"
                icon={<FiDollarSign className="w-5 h-5" />}
                {...register('currency')}
                error={errors.currency?.message}
                as="select"
              >
                {currencies?.map((currency) => (
                  <option key={currency} value={currency}>
                    {currency}
                  </option>
                ))}
              </Input>
            </div>

            {/* IBAN and BIC */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Input
                  label="Beneficiary IBAN"
                  placeholder="Enter IBAN"
                  icon={<FiCreditCard className="w-5 h-5" />}
                  endIcon={
                    ibanValidating ? (
                      <LoadingSpinner size="sm" />
                    ) : ibanValid === true ? (
                      <FiCheckCircle className="w-5 h-5 text-green-500" />
                    ) : ibanValid === false ? (
                      <FiAlertCircle className="w-5 h-5 text-red-500" />
                    ) : null
                  }
                  {...register('beneficiary_iban')}
                  error={errors.beneficiary_iban?.message}
                />
                {bankInfo && (
                  <p className="mt-1 text-sm text-gray-600">
                    Bank: {bankInfo.bank_name}
                  </p>
                )}
              </div>

              <Input
                label="Beneficiary BIC"
                placeholder="Enter BIC"
                icon={<FiCreditCard className="w-5 h-5" />}
                {...register('beneficiary_bic')}
                error={errors.beneficiary_bic?.message}
              />
            </div>

            {/* Amount and Priority */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Amount"
                type="number"
                step="0.01"
                placeholder="0.00"
                icon={<FiDollarSign className="w-5 h-5" />}
                {...register('amount', { valueAsNumber: true })}
                error={errors.amount?.message}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <select
                  {...register('priority')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={TransferPriority.NORMAL}>Normal</option>
                  <option value={TransferPriority.URGENT}>Urgent</option>
                  <option value={TransferPriority.EXPRESS}>Express</option>
                </select>
                {errors.priority && (
                  <p className="mt-1 text-sm text-red-600">{errors.priority.message}</p>
                )}
              </div>
            </div>

            {/* Transfer Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Transfer Type
              </label>
              <select
                {...register('transfer_type')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={TransferType.SWIFT}>SWIFT</option>
                <option value={TransferType.IBAN}>IBAN</option>
                <option value={TransferType.MOJALOOP}>Mojaloop</option>
              </select>
              {errors.transfer_type && (
                <p className="mt-1 text-sm text-red-600">{errors.transfer_type.message}</p>
              )}
            </div>

            {/* Description */}
            <Input
              label="Description"
              placeholder="Enter transfer description"
              {...register('description')}
              error={errors.description?.message}
            />

            {/* Submit Button */}
            <div className="flex justify-end space-x-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/dashboard')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                loading={isSubmitting || createTransferMutation.isLoading}
                icon={<FiSend className="w-4 h-4" />}
              >
                Create Transfer
              </Button>
            </div>
          </form>
        </motion.div>
      </div>
    </>
  );
};

export default TransferForm;