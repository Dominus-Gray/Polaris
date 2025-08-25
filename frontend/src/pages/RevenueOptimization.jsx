import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://polaris-requirements.preview.emergentagent.com/api';

function RevenueOptimization() {
  const navigate = useNavigate();
  const [revenueData, setRevenueData] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedService, setSelectedService] = useState(null);

  useEffect(() => {
    loadRevenueData();
  }, []);

  const loadRevenueData = async () => {
    try {
      const [revenueRes, marketRes] = await Promise.all([
        axios.get(`${API}/provider/revenue/analytics`),
        axios.get(`${API}/provider/revenue/market-analysis`)
      ]);

      setRevenueData(revenueRes.data);
      setMarketData(marketRes.data);
    } catch (error) {
      console.error('Error loading revenue data:', error);
      // Mock data for demo
      setRevenueData({
        current_month_revenue: 8500,
        last_month_revenue: 7200,
        year_to_date: 45600,
        projected_annual: 102000,
        average_project_value: 2800,
        conversion_rate: 24,
        response_rate: 78,
        client_satisfaction: 4.7,
        active_proposals: 12,
        won_proposals: 8,
        lost_proposals: 4,
        pipeline_value: 34000,
        monthly_trends: [
          { month: 'Jan', revenue: 6200, projects: 3 },
          { month: 'Feb', revenue: 7800, projects: 4 },
          { month: 'Mar', revenue: 8500, projects: 5 },
          { month: 'Apr', revenue: 9200, projects: 4 },
          { month: 'May', revenue: 7600, projects: 3 },
          { month: 'Jun', revenue: 8500, projects: 4 }
        ],
        top_services: [
          { name: 'Business Formation', revenue: 18500, projects: 12, avg_value: 1542 },
          { name: 'Financial Planning', revenue: 15200, projects: 8, avg_value: 1900 },
          { name: 'Legal Compliance', revenue: 12800, projects: 6, avg_value: 2133 }
        ]
      });

      setMarketData({
        market_rates: {
          'Business Formation': { min: 800, max: 3500, average: 1650, your_rate: 1542 },
          'Financial Planning': { min: 1200, max: 5000, average: 2200, your_rate: 1900 },
          'Legal Compliance': { min: 1500, max: 4500, average: 2400, your_rate: 2133 }
        },
        demand_trends: {
          'Business Formation': { trend: 'increasing', demand_score: 85, competition: 'moderate' },
          'Financial Planning': { trend: 'stable', demand_score: 72, competition: 'high' },
          'Legal Compliance': { trend: 'increasing', demand_score: 91, competition: 'low' }
        },
        optimization_opportunities: [
          {
            service: 'Legal Compliance',
            current_rate: 2133,
            suggested_rate: 2400,
            potential_increase: 12.5,
            reasoning: 'Below market average with high demand and low competition'
          },
          {
            service: 'Business Formation',
            current_rate: 1542,
            suggested_rate: 1800,
            potential_increase: 16.7,
            reasoning: 'Strong demand trend and moderate competition allow for premium pricing'
          }
        ],
        seasonal_insights: {
          'Q1': { revenue_multiplier: 1.2, best_services: ['Business Formation', 'Tax Planning'] },
          'Q2': { revenue_multiplier: 0.9, best_services: ['Financial Planning', 'Legal Compliance'] },
          'Q3': { revenue_multiplier: 0.8, best_services: ['HR Services', 'Performance Management'] },
          'Q4': { revenue_multiplier: 1.3, best_services: ['Tax Planning', 'Year-end Financial'] }
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const getPercentageChange = (current, previous) => {
    if (!previous) return 0;
    return ((current - previous) / previous * 100).toFixed(1);
  };

  const getTrendIcon = (change) => {
    if (change > 0) return <span className="text-green-500">↗️</span>;
    if (change < 0) return <span className="text-red-500">↘️</span>;
    return <span className="text-slate-500">→</span>;
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-7xl">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/2 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-32 bg-slate-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-7xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Revenue Optimization Center</h1>
            <p className="text-green-100">Maximize your earnings with data-driven insights and market intelligence</p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold mb-2">${revenueData?.current_month_revenue?.toLocaleString()}</div>
            <div className="text-green-200">This Month</div>
            <div className="flex items-center gap-2 mt-2 justify-end">
              {getTrendIcon(getPercentageChange(revenueData?.current_month_revenue, revenueData?.last_month_revenue))}
              <span className="text-sm text-green-200">
                {getPercentageChange(revenueData?.current_month_revenue, revenueData?.last_month_revenue)}% vs last month
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">YTD Revenue</h3>
            <span className="text-2xl">📈</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">${revenueData?.year_to_date?.toLocaleString()}</div>
          <div className="text-sm text-green-600">On track for ${revenueData?.projected_annual?.toLocaleString()}</div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Avg Project Value</h3>
            <span className="text-2xl">💰</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">${revenueData?.average_project_value?.toLocaleString()}</div>
          <div className="text-sm text-slate-600">Per completed project</div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Conversion Rate</h3>
            <span className="text-2xl">🎯</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">{revenueData?.conversion_rate}%</div>
          <div className="text-sm text-slate-600">Proposals to wins</div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Pipeline Value</h3>
            <span className="text-2xl">🔮</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">${revenueData?.pipeline_value?.toLocaleString()}</div>
          <div className="text-sm text-slate-600">{revenueData?.active_proposals} active proposals</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm mb-8">
        <div className="border-b border-slate-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Revenue Overview', icon: '📊' },
              { id: 'pricing', label: 'Pricing Optimization', icon: '💲' },
              { id: 'market', label: 'Market Analysis', icon: '📈' },
              { id: 'forecasting', label: 'Revenue Forecasting', icon: '🔮' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Revenue Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-8">
              {/* Revenue Trends Chart */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-4">Monthly Revenue Trends</h3>
                  <div className="space-y-3">
                    {revenueData?.monthly_trends?.map((month, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="font-medium text-slate-900">{month.month}</div>
                          <div className="text-sm text-slate-600">{month.projects} projects</div>
                        </div>
                        <div className="text-lg font-semibold text-green-600">${month.revenue.toLocaleString()}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-4">Top Performing Services</h3>
                  <div className="space-y-3">
                    {revenueData?.top_services?.map((service, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-slate-900">{service.name}</h4>
                          <div className="text-lg font-semibold text-green-600">${service.revenue.toLocaleString()}</div>
                        </div>
                        <div className="flex items-center justify-between text-sm text-slate-600">
                          <span>{service.projects} projects</span>
                          <span>Avg: ${service.avg_value}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h4 className="font-semibold text-green-800 mb-4">Proposals Won</h4>
                  <div className="text-3xl font-bold text-green-600 mb-2">{revenueData?.won_proposals}</div>
                  <div className="text-sm text-green-700">Out of {revenueData?.won_proposals + revenueData?.lost_proposals} submitted</div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h4 className="font-semibold text-blue-800 mb-4">Response Rate</h4>
                  <div className="text-3xl font-bold text-blue-600 mb-2">{revenueData?.response_rate}%</div>
                  <div className="text-sm text-blue-700">Above industry average</div>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                  <h4 className="font-semibold text-purple-800 mb-4">Client Satisfaction</h4>
                  <div className="text-3xl font-bold text-purple-600 mb-2">{revenueData?.client_satisfaction}/5.0</div>
                  <div className="text-sm text-purple-700">Excellent rating</div>
                </div>
              </div>
            </div>
          )}

          {/* Pricing Optimization Tab */}
          {activeTab === 'pricing' && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-6">Market Rate Comparison</h3>
                  <div className="space-y-4">
                    {Object.entries(marketData?.market_rates || {}).map(([service, rates]) => (
                      <div key={service} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium text-slate-900">{service}</h4>
                          <div className={`text-sm font-medium ${
                            rates.your_rate >= rates.average ? 'text-green-600' : 'text-yellow-600'
                          }`}>
                            Your Rate: ${rates.your_rate}
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm text-slate-600">
                            <span>Market Range</span>
                            <span>${rates.min} - ${rates.max}</span>
                          </div>
                          <div className="flex justify-between text-sm text-slate-600">
                            <span>Market Average</span>
                            <span>${rates.average}</span>
                          </div>
                          
                          {/* Rate Comparison Bar */}
                          <div className="relative h-2 bg-slate-200 rounded-full mt-3">
                            <div 
                              className="absolute h-2 bg-green-500 rounded-full"
                              style={{ 
                                left: `${((rates.your_rate - rates.min) / (rates.max - rates.min)) * 100}%`,
                                width: '4px'
                              }}
                            ></div>
                            <div 
                              className="absolute h-2 bg-blue-500 rounded-full"
                              style={{ 
                                left: `${((rates.average - rates.min) / (rates.max - rates.min)) * 100}%`,
                                width: '2px'
                              }}
                            ></div>
                          </div>
                          
                          <div className="flex justify-between text-xs text-slate-500">
                            <span>Min</span>
                            <span>Max</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-6">Optimization Opportunities</h3>
                  <div className="space-y-4">
                    {marketData?.optimization_opportunities?.map((opportunity, index) => (
                      <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium text-yellow-800">{opportunity.service}</h4>
                          <div className="text-green-600 font-semibold">+{opportunity.potential_increase}%</div>
                        </div>
                        
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-600">Current Rate:</span>
                            <span className="font-medium">${opportunity.current_rate}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">Suggested Rate:</span>
                            <span className="font-medium text-green-600">${opportunity.suggested_rate}</span>
                          </div>
                        </div>
                        
                        <p className="text-xs text-yellow-700 mt-3">{opportunity.reasoning}</p>
                        
                        <button 
                          className="btn btn-sm btn-primary mt-3"
                          onClick={() => navigate(`/provider/services/edit/${opportunity.service}`)}
                        >
                          Update Pricing
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Market Analysis Tab */}
          {activeTab === 'market' && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-6">Demand Trends</h3>
                  <div className="space-y-4">
                    {Object.entries(marketData?.demand_trends || {}).map(([service, trend]) => (
                      <div key={service} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium text-slate-900">{service}</h4>
                          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                            trend.trend === 'increasing' ? 'bg-green-100 text-green-800' :
                            trend.trend === 'decreasing' ? 'bg-red-100 text-red-800' :
                            'bg-slate-100 text-slate-800'
                          }`}>
                            {trend.trend}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <div className="text-slate-600">Demand Score</div>
                            <div className="text-lg font-semibold text-blue-600">{trend.demand_score}/100</div>
                          </div>
                          <div>
                            <div className="text-slate-600">Competition</div>
                            <div className={`font-medium capitalize ${
                              trend.competition === 'low' ? 'text-green-600' :
                              trend.competition === 'moderate' ? 'text-yellow-600' :
                              'text-red-600'
                            }`}>
                              {trend.competition}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-6">Seasonal Insights</h3>
                  <div className="space-y-4">
                    {Object.entries(marketData?.seasonal_insights || {}).map(([quarter, insights]) => (
                      <div key={quarter} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium text-slate-900">{quarter}</h4>
                          <div className={`text-sm font-medium ${
                            insights.revenue_multiplier > 1 ? 'text-green-600' : 'text-slate-600'
                          }`}>
                            {insights.revenue_multiplier}x Revenue
                          </div>
                        </div>
                        
                        <div>
                          <div className="text-sm text-slate-600 mb-2">High-demand services:</div>
                          <div className="flex flex-wrap gap-2">
                            {insights.best_services.map((service, index) => (
                              <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                                {service}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Revenue Forecasting Tab */}
          {activeTab === 'forecasting' && (
            <div className="space-y-8">
              <RevenueForecastingTools revenueData={revenueData} marketData={marketData} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Revenue Forecasting Tools Component
function RevenueForecastingTools({ revenueData, marketData }) {
  const [forecastInputs, setForecastInputs] = useState({
    target_monthly_revenue: revenueData?.current_month_revenue || 0,
    price_increase_percentage: 0,
    new_services_count: 0,
    marketing_investment: 0
  });

  const [forecast, setForecast] = useState(null);

  const calculateForecast = () => {
    const currentRevenue = revenueData?.current_month_revenue || 0;
    const priceIncreaseMultiplier = 1 + (forecastInputs.price_increase_percentage / 100);
    const newServicesRevenue = forecastInputs.new_services_count * (revenueData?.average_project_value || 0) * 0.5;
    const marketingMultiplier = 1 + (forecastInputs.marketing_investment / 10000) * 0.1;

    const projectedMonthly = (currentRevenue * priceIncreaseMultiplier * marketingMultiplier) + newServicesRevenue;
    const projectedAnnual = projectedMonthly * 12;

    setForecast({
      monthly: projectedMonthly,
      annual: projectedAnnual,
      increase_percentage: ((projectedMonthly - currentRevenue) / currentRevenue) * 100
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-6">Revenue Forecasting</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Target Monthly Revenue
            </label>
            <input
              type="number"
              className="w-full input"
              value={forecastInputs.target_monthly_revenue}
              onChange={(e) => setForecastInputs(prev => ({ 
                ...prev, 
                target_monthly_revenue: parseInt(e.target.value) || 0 
              }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Price Increase (%)
            </label>
            <input
              type="number"
              className="w-full input"
              value={forecastInputs.price_increase_percentage}
              onChange={(e) => setForecastInputs(prev => ({ 
                ...prev, 
                price_increase_percentage: parseFloat(e.target.value) || 0 
              }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              New Services to Launch
            </label>
            <input
              type="number"
              className="w-full input"
              value={forecastInputs.new_services_count}
              onChange={(e) => setForecastInputs(prev => ({ 
                ...prev, 
                new_services_count: parseInt(e.target.value) || 0 
              }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Marketing Investment ($)
            </label>
            <input
              type="number"
              className="w-full input"
              value={forecastInputs.marketing_investment}
              onChange={(e) => setForecastInputs(prev => ({ 
                ...prev, 
                marketing_investment: parseFloat(e.target.value) || 0 
              }))}
            />
          </div>

          <button 
            className="btn btn-primary w-full"
            onClick={calculateForecast}
          >
            Calculate Forecast
          </button>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-6">Projected Results</h3>
        
        {forecast ? (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h4 className="font-semibold text-green-800 mb-4">Monthly Projection</h4>
              <div className="text-3xl font-bold text-green-600 mb-2">
                ${forecast.monthly.toLocaleString()}
              </div>
              <div className={`text-sm ${
                forecast.increase_percentage > 0 ? 'text-green-700' : 'text-red-700'
              }`}>
                {forecast.increase_percentage > 0 ? '+' : ''}{forecast.increase_percentage.toFixed(1)}% change
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h4 className="font-semibold text-blue-800 mb-4">Annual Projection</h4>
              <div className="text-3xl font-bold text-blue-600 mb-2">
                ${forecast.annual.toLocaleString()}
              </div>
              <div className="text-sm text-blue-700">
                Based on current growth trajectory
              </div>
            </div>

            <div className="border rounded-lg p-4">
              <h5 className="font-medium text-slate-900 mb-3">Recommendations</h5>
              <ul className="space-y-2 text-sm text-slate-600">
                <li>• Focus on high-demand services with low competition</li>
                <li>• Consider gradual price increases for established services</li>
                <li>• Invest in marketing during seasonal peak periods</li>
                <li>• Monitor conversion rates after pricing changes</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center">
            <div className="text-4xl mb-4">📊</div>
            <p className="text-slate-600">Enter your forecasting parameters and click calculate to see projections</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default RevenueOptimization;