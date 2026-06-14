import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SupabaseService } from '../../services/supabase.service';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './products.component.html',
  styleUrl: './products.component.scss'
})
export class ProductsComponent implements OnInit {
  shopId = '';
  shop: any = null;
  products: any[] = [];
  loading = true;
  saving = false;
  deleting: Record<string, boolean> = {};

  showAddForm = false;
  editingId: string | null = null;

  newProduct = {
    name: '',
    unit: 'unit',
    cost_price: 0,
    selling_price: 0,
    low_stock_threshold: 10
  };

  editProduct: any = null;

  units = ['unit', 'pack', 'bottle', 'bag', 'carton', 'tin', 'litre', 'kg', 'dozen'];

  stockEditing: Record<string, number> = {};
stockSaving: Record<string, boolean> = {};

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
    const [shops, products] = await Promise.all([
      this.supabase.getShops('00000000-0000-0000-0000-000000000001'),
      this.supabase.getProducts(this.shopId)
    ]);
    this.shop = shops.find((s: any) => s.id === this.shopId);
    this.products = products || [];
  }

  startEdit(product: any) {
    this.editingId = product.id;
    this.editProduct = {
      id: product.id,
      shop_id: this.shopId,
      name: product.name,
      unit: product.unit,
      cost_price: product.cost_price,
      selling_price: product.selling_price,
      low_stock_threshold: product.low_stock_threshold
    };
  }

  cancelEdit() {
    this.editingId = null;
    this.editProduct = null;
  }

  async saveEdit() {
    if (!this.editProduct) return;
    this.saving = true;
    try {
      await this.supabase.upsertProduct(this.editProduct);
      await this.loadAll();
      this.cancelEdit();
    } finally {
      this.saving = false;
    }
  }

  async addProduct() {
    if (!this.newProduct.name.trim()) return;
    this.saving = true;
    try {
      const product = {
        ...this.newProduct,
        shop_id: this.shopId,
        name: this.newProduct.name.trim()
      };
      await this.supabase.upsertProduct(product);
      await this.loadAll();
      this.resetNewProduct();
      this.showAddForm = false;
    } finally {
      this.saving = false;
    }
  }

  async deleteProduct(productId: string) {
    this.deleting[productId] = true;
    try {
      await this.supabase.deleteProduct(productId);
      await this.loadAll();
    } finally {
      this.deleting[productId] = false;
    }
  }

  async saveStock(productId: string) {
    this.stockSaving[productId] = true;
    try {
      await this.supabase.updateStock(
        this.shopId,
        productId,
        this.stockEditing[productId]
      );
      await this.loadAll();
    } finally {
      this.stockSaving[productId] = false;
    }
  }

  resetNewProduct() {
    this.newProduct = {
      name: '',
      unit: 'unit',
      cost_price: 0,
      selling_price: 0,
      low_stock_threshold: 10
    };
  }

  get margin(): number {
    if (!this.editProduct?.selling_price) return 0;
    return Math.round(
      ((this.editProduct.selling_price - this.editProduct.cost_price)
      / this.editProduct.selling_price) * 100
    );
  }

  productMargin(product: any): number {
    if (!product.selling_price) return 0;
    return Math.round(
      ((product.selling_price - product.cost_price)
      / product.selling_price) * 100
    );
  }

  getStock(product: any): number {
    return product.inventory?.[0]?.quantity ?? 0;
  }
}
