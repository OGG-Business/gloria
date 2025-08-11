import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { motion } from 'framer-motion';
import { FiMail, FiLock, FiEye, FiEyeOff, FiShield } from 'react-icons/fi';
import { toast } from 'react-hot-toast';
import { Helmet } from 'react-helmet-async';

import { useAuth } from '../hooks/useAuth';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

interface LoginFormData {
  username: string;
  password: string;
  mfa_code?: string;
}

const schema = yup.object({
  username: yup.string().required('Username is required'),
  password: yup.string().required('Password is required'),
  mfa_code: yup.string().when('$showMfa', {
    is: true,
    then: yup.string().required('MFA code is required').length(6, 'MFA code must be 6 digits'),
  }),
}).required();

const Login: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showMfa, setShowMfa] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<LoginFormData>({
    resolver: yupResolver(schema),
    context: { showMfa },
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      await login(data);
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (error: any) {
      if (error.response?.status === 401) {
        if (error.response.data?.requires_mfa) {
          setShowMfa(true);
          toast.error('Please enter your MFA code');
        } else {
          toast.error('Invalid username or password');
        }
      } else {
        toast.error('Login failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Helmet>
        <title>Login - Banking Transfer Platform</title>
      </Helmet>
      
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md w-full space-y-8"
        >
          {/* Header */}
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-6"
            >
              <FiShield className="w-8 h-8 text-white" />
            </motion.div>
            
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome Back
            </h2>
            <p className="text-gray-600">
              Sign in to your Banking Transfer account
            </p>
          </div>

          {/* Login Form */}
          <motion.form
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow-xl p-8"
            onSubmit={handleSubmit(onSubmit)}
          >
            <div className="space-y-6">
              {/* Username */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  icon={<FiMail className="w-5 h-5" />}
                  {...register('username')}
                  error={errors.username?.message}
                />
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  icon={<FiLock className="w-5 h-5" />}
                  endIcon={
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
                    </button>
                  }
                  {...register('password')}
                  error={errors.password?.message}
                />
              </div>

              {/* MFA Code */}
              {showMfa && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <label htmlFor="mfa_code" className="block text-sm font-medium text-gray-700 mb-2">
                    MFA Code
                  </label>
                  <Input
                    id="mfa_code"
                    type="text"
                    placeholder="Enter 6-digit code"
                    icon={<FiShield className="w-5 h-5" />}
                    {...register('mfa_code')}
                    error={errors.mfa_code?.message}
                    maxLength={6}
                  />
                </motion.div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                loading={isLoading}
                disabled={isLoading}
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </Button>
            </div>

            {/* Additional Links */}
            <div className="mt-6 text-center">
              <a
                href="#"
                className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
              >
                Forgot your password?
              </a>
            </div>
          </motion.form>

          {/* Footer */}
          <div className="text-center">
            <p className="text-sm text-gray-500">
              Don't have an account?{' '}
              <a
                href="#"
                className="text-blue-600 hover:text-blue-500 font-medium transition-colors"
              >
                Contact your bank
              </a>
            </p>
          </div>
        </motion.div>
      </div>
    </>
  );
};

export default Login;