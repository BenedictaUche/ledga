import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { SupabaseService } from '../../services/supabase.service';

@Component({
  selector: 'app-inventory',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './inventory.component.html',
  styleUrl: './inventory.component.scss'
})
export class InventoryComponent implements OnInit {
  shopId = '';
  shop: any = null;
  inventory: any[] = [];
  loading = true;

  constructor(
    private route: ActivatedRoute,
    private supabase: SupabaseService
  ) {}

  async ngOnInit() {
    this.shopId = this.route.snapshot.paramMap.get('id') || '';
    await this.loadAll();
    this.loading = false;
  }

  async loadAll() {
    const [shops, inventory] = await Promise.all([
      this.supabase.getShops('00000000-0000-0000-0000-000000000001'),
      this.supabase.getInventory(this.shopId)
    ]);
    this.shop = shops.find((s: any) => s.id === this.shopId);
    this.inventory = inventory || [];
  }

  stockStatus(item: any): 'critical' | 'low' | 'ok' {
    const qty = item.quantity;
    const threshold = item.products?.low_stock_threshold || 10;
    if (qty === 0) return 'critical';
    if (qty <= threshold) return 'low';
    return 'ok';
  }

  stockLabel(item: any): string {
    const status = this.stockStatus(item);
    if (status === 'critical') return 'Out of stock';
    if (status === 'low') return 'Low stock';
    return 'In stock';
  }

  stockWidth(item: any): number {
    const threshold = item.products?.low_stock_threshold || 10;
    const max = threshold * 5;
    return Math.min(100, Math.round((item.quantity / max) * 100));
  }

  get criticalCount(): number {
    return this.inventory.filter(i => this.stockStatus(i) === 'critical').length;
  }

  get lowCount(): number {
    return this.inventory.filter(i => this.stockStatus(i) === 'low').length;
  }
}
