import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ShopDetailComponent } from './pages/shop-detail/shop-detail.component';
import { InventoryComponent } from './pages/inventory/inventory.component';
import { ProductsComponent } from './pages/products/products.component';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'shop/:id', component: ShopDetailComponent },
  { path: 'shop/:id/inventory', component: InventoryComponent },
  { path: 'shop/:id/products', component: ProductsComponent },
  { path: '**', redirectTo: '' }
];
