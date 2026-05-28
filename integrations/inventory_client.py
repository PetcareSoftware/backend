import os
import requests


class InventoryInsufficientStock(Exception):
    pass


class InventoryNotFound(Exception):
    pass


class InventoryUnavailable(Exception):
    pass


class InventoryClient:
    """Cliente HTTP encapsulado para Backend 2. Timeout obligatorio: 3 segundos."""
    timeout = 3

    def __init__(self, base_url=None):
        self.base_url = (base_url or os.environ.get('BACKEND2_INVENTORY_URL') or '').rstrip('/')

    def _request(self, method, path, payload=None):
        if not self.base_url:
            raise InventoryUnavailable('Backend 2 no configurado.')
        try:
            response = requests.request(method, f'{self.base_url}{path}', json=payload, timeout=self.timeout)
        except requests.Timeout as exc:
            raise InventoryUnavailable('Timeout al consultar Backend 2.') from exc
        except requests.RequestException as exc:
            raise InventoryUnavailable('Backend 2 no disponible.') from exc
        if response.status_code == 404:
            raise InventoryNotFound('supply_id inexistente en catálogo.')
        if response.status_code == 409:
            detail = response.json().get('detail', 'Stock insuficiente.') if response.content else 'Stock insuficiente.'
            raise InventoryInsufficientStock(detail)
        if response.status_code >= 500:
            raise InventoryUnavailable('Backend 2 devolvió error 5xx.')
        response.raise_for_status()
        return response.json() if response.content else {}

    def _post(self, path, payload):
        return self._request('POST', path, payload)

    def _get(self, path):
        return self._request('GET', path)

    def get_supply(self, supply_id):
        """Obtiene el insumo individual según el contrato Backend 1 ↔ Backend 2."""
        return self._get(f'/supplies/{supply_id}/')

    def check_availability(self, supply_id, quantity):
        """Valida disponibilidad de un insumo individual y devuelve sus metadatos."""
        supplies = self.check_supplies([{'supply_id': supply_id, 'quantity': quantity}])
        return supplies[0] if supplies else {'supply_id': str(supply_id), 'quantity': str(quantity)}

    def deduct_stock(self, supply_id, quantity, ref_id):
        """Descuenta stock vinculando el movimiento al ref_id de consulta/evento."""
        supplies = self.consume_supplies([{'supply_id': supply_id, 'quantity': quantity, 'ref_id': ref_id}])
        return supplies[0] if supplies else {'supply_id': str(supply_id), 'quantity': str(quantity), 'ref_id': str(ref_id)}

    def check_supplies(self, supplies):
        return self._post('/supplies/check/', {'supplies': self._normalize(supplies)}).get('supplies', [])

    def consume_supplies(self, supplies):
        return self._post('/supplies/consume/', {'supplies': self._normalize(supplies)}).get('supplies', [])

    def _normalize(self, supplies):
        normalized = []
        for item in supplies:
            data = {'supply_id': str(item['supply_id']), 'quantity': str(item['quantity'])}
            if item.get('ref_id') is not None:
                data['ref_id'] = str(item['ref_id'])
            normalized.append(data)
        return normalized
