import { Injectable } from '@angular/core';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class SupabaseService {
  private supabase: SupabaseClient;

  constructor() {
    this.supabase = createClient(environment.supabaseUrl, environment.supabaseKey);
  }

  get client() {
    return this.supabase;
  }

  async getShops(operatorId: string) {
    const { data, error } = await this.supabase
      .from('shops')
      .select('*')
      .eq('operator_id', operatorId)
      .eq('is_active', true);
    if (error) throw error;
    return data;
  }

  async getInventory(shopId: string) {
    const { data, error } = await this.supabase
      .from('inventory')
      .select('*, products(name, unit, selling_price, cost_price, low_stock_threshold)')
      .eq('shop_id', shopId)
      .order('quantity', { ascending: true });
    if (error) throw error;
    return data;
  }

  async getTodaySummary(shopId: string) {
    const today = new Date().toISOString().split('T')[0];
    const { data, error } = await this.supabase
      .from('business_days')
      .select('*')
      .eq('shop_id', shopId)
      .eq('date', today);
    if (error) throw error;
    return data?.[0] || null;
  }

  async getProducts(shopId: string) {
    const { data, error } = await this.supabase
      .from('products')
      .select('*, inventory(quantity)')
      .eq('shop_id', shopId)
      .order('name', { ascending: true });
    if (error) throw error;
    return data;
  }

  async upsertProduct(product: any) {
    const { data, error } = await this.supabase
      .from('products')
      .upsert(product, { onConflict: 'id' })
      .select();
    if (error) throw error;
    return data;
  }

  async deleteProduct(productId: string) {
    const { error } = await this.supabase
      .from('products')
      .delete()
      .eq('id', productId);
    if (error) throw error;
  }

  async getShopTransactions(shopId: string) {
    const today = new Date().toISOString().split('T')[0];
    const { data, error } = await this.supabase
      .from('transactions')
      .select('*, products(name, unit)')
      .eq('shop_id', shopId)
      .gte('created_at', today)
      .order('created_at', { ascending: false });
    if (error) throw error;
    return data;
  }

  async updateStock(shopId: string, productId: string, quantity: number) {
    const { error } = await this.supabase
      .from('inventory')
      .upsert({
        shop_id: shopId,
        product_id: productId,
        quantity: quantity
      }, { onConflict: 'shop_id,product_id' });
    if (error) throw error;
  }

  async getPendingExceptions(operatorId: string) {
    const { data: shops } = await this.supabase
      .from('shops')
      .select('id')
      .eq('operator_id', operatorId);

    if (!shops?.length) return [];

    const shopIds = shops.map(s => s.id);
    const { data, error } = await this.supabase
      .from('exceptions')
      .select('*, shops(name, owner_name)')
      .in('shop_id', shopIds)
      .eq('status', 'pending')
      .order('created_at', { ascending: false });
    if (error) throw error;
    return data;
  }

  async resolveException(exceptionId: string, operatorId: string, status: 'resolved' | 'dismissed') {
    const { data, error } = await this.supabase
      .from('exceptions')
      .update({
        status,
        resolved_by: operatorId,
        resolved_at: new Date().toISOString()
      })
      .eq('id', exceptionId);
    if (error) throw error;
    return data;
  }

  async getCreditLedger(shopId: string) {
    const { data, error } = await this.supabase
      .from('customers')
      .select('*, credit_ledger(*)')
      .eq('shop_id', shopId)
      .gt('total_credit_owed', 0)
      .order('total_credit_owed', { ascending: false });
    if (error) throw error;
    return data;
  }
}
