import { classify, isDeprecatedRemoval } from '../src/classify';
import { SchemaChange } from '../src/types';

describe('Classification Logic', () => {
  
  describe('Breaking Changes', () => {
    test('should classify schema removal as breaking', () => {
      const changes: SchemaChange[] = [{
        type: 'remove',
        path: ['users.yaml'],
        oldValue: { type: 'object' },
        classificationHint: 'schema_removed'
      }];
      
      const result = classify(changes);
      expect(result.breaking).toHaveLength(1);
      expect(result.breaking[0]).toEqual(changes[0]);
    });
    
    test('should classify endpoint removal as breaking', () => {
      const changes: SchemaChange[] = [{
        type: 'remove',
        path: ['paths', '/users', 'get'],
        oldValue: { summary: 'Get users' },
        classificationHint: 'endpoint_removed'
      }];
      
      const result = classify(changes);
      expect(result.breaking).toHaveLength(1);
    });
    
    test('should classify required field addition as breaking', () => {
      const changes: SchemaChange[] = [{
        type: 'add',
        path: ['components', 'schemas', 'User', 'required'],
        newValue: ['newField'],
        classificationHint: 'required_field_added'
      }];
      
      const result = classify(changes);
      expect(result.breaking).toHaveLength(1);
    });
    
    test('should classify property removal as breaking', () => {
      const changes: SchemaChange[] = [{
        type: 'remove',
        path: ['components', 'schemas', 'User', 'properties', 'username'],
        oldValue: { type: 'string' },
        classificationHint: 'property_removed'
      }];
      
      const result = classify(changes);
      expect(result.breaking).toHaveLength(1);
    });
    
    test('should classify type change as breaking', () => {
      const changes: SchemaChange[] = [{
        type: 'modify',
        path: ['components', 'schemas', 'User', 'properties', 'age'],
        oldValue: { type: 'string' },
        newValue: { type: 'number' },
        classificationHint: 'type_changed'
      }];
      
      const result = classify(changes);
      expect(result.breaking).toHaveLength(1);
    });
  });
  
  describe('Additive Changes', () => {
    test('should classify new endpoint as additive', () => {
      const changes: SchemaChange[] = [{
        type: 'add',
        path: ['paths', '/users/bulk', 'post'],
        newValue: { summary: 'Bulk create users' },
        classificationHint: 'endpoint_added'
      }];
      
      const result = classify(changes);
      expect(result.additive).toHaveLength(1);
      expect(result.breaking).toHaveLength(0);
    });
    
    test('should classify new optional property as additive', () => {
      const changes: SchemaChange[] = [{
        type: 'add',
        path: ['components', 'schemas', 'User', 'properties', 'nickname'],
        newValue: { type: 'string' },
        classificationHint: 'property_added'
      }];
      
      const result = classify(changes);
      expect(result.additive).toHaveLength(1);
    });
    
    test('should classify new response code as additive', () => {
      const changes: SchemaChange[] = [{
        type: 'add',
        path: ['paths', '/users', 'get', 'responses', '201'],
        newValue: { description: 'Created' },
        classificationHint: 'response_added'
      }];
      
      const result = classify(changes);
      expect(result.additive).toHaveLength(1);
    });
  });
  
  describe('Documentation Changes', () => {
    test('should classify description changes as docs-only', () => {
      const changes: SchemaChange[] = [{
        type: 'modify',
        path: ['components', 'schemas', 'User', 'properties', 'username', 'description'],
        oldValue: 'User name',
        newValue: 'Username for login'
      }];
      
      const result = classify(changes);
      expect(result.docsOnly).toHaveLength(1);
      expect(result.breaking).toHaveLength(0);
    });
    
    test('should classify example changes as docs-only', () => {
      const changes: SchemaChange[] = [{
        type: 'modify',
        path: ['components', 'schemas', 'User', 'example'],
        oldValue: { username: 'john' },
        newValue: { username: 'jane' }
      }];
      
      const result = classify(changes);
      expect(result.docsOnly).toHaveLength(1);
    });
    
    test('should classify summary changes as docs-only', () => {
      const changes: SchemaChange[] = [{
        type: 'modify',
        path: ['paths', '/users', 'get', 'summary'],
        oldValue: 'Get users',
        newValue: 'Retrieve all users'
      }];
      
      const result = classify(changes);
      expect(result.docsOnly).toHaveLength(1);
    });
  });
  
  describe('Refactor Changes', () => {
    test('should classify x-internal changes as refactor', () => {
      const changes: SchemaChange[] = [{
        type: 'modify',
        path: ['components', 'schemas', 'User', 'x-internal-note'],
        oldValue: 'old note',
        newValue: 'new note'
      }];
      
      const result = classify(changes);
      expect(result.refactor).toHaveLength(1);
    });
    
    test('should classify x-codegen changes as refactor', () => {
      const changes: SchemaChange[] = [{
        type: 'add',
        path: ['components', 'schemas', 'User', 'x-codegen-config'],
        newValue: { generate: true }
      }];
      
      const result = classify(changes);
      expect(result.refactor).toHaveLength(1);
    });
  });
  
  describe('Mixed Changes', () => {
    test('should correctly classify multiple change types', () => {
      const changes: SchemaChange[] = [
        {
          type: 'remove',
          path: ['paths', '/legacy', 'get'],
          oldValue: {},
          classificationHint: 'endpoint_removed'
        },
        {
          type: 'add',
          path: ['paths', '/new-endpoint', 'post'],
          newValue: {},
          classificationHint: 'endpoint_added'
        },
        {
          type: 'modify',
          path: ['info', 'description'],
          oldValue: 'Old description',
          newValue: 'New description'
        }
      ];
      
      const result = classify(changes);
      expect(result.breaking).toHaveLength(1);
      expect(result.additive).toHaveLength(1);
      expect(result.docsOnly).toHaveLength(1);
      expect(result.refactor).toHaveLength(0);
    });
  });
});

describe('Deprecation Logic', () => {
  const mockConfig = {
    docsOnlyPatterns: ['description'],
    ignoreOrdering: true,
    deprecationFields: ['x-status', 'x-sunset', 'deprecated'],
    deprecationWindowDays: 90,
    enforcement: 'warn' as const
  };
  
  test('should detect properly deprecated removal with x-status', () => {
    const change: SchemaChange = {
      type: 'remove',
      path: ['components', 'schemas', 'User', 'properties', 'oldField'],
      oldValue: {
        type: 'string',
        'x-status': 'deprecated'
      }
    };
    
    expect(isDeprecatedRemoval(change, mockConfig)).toBe(true);
  });
  
  test('should detect properly deprecated removal with deprecated flag', () => {
    const change: SchemaChange = {
      type: 'remove',
      path: ['components', 'schemas', 'User', 'properties', 'oldField'],
      oldValue: {
        type: 'string',
        deprecated: true
      }
    };
    
    expect(isDeprecatedRemoval(change, mockConfig)).toBe(true);
  });
  
  test('should detect properly deprecated removal with x-sunset', () => {
    const change: SchemaChange = {
      type: 'remove',
      path: ['components', 'schemas', 'User', 'properties', 'oldField'],
      oldValue: {
        type: 'string',
        'x-sunset': '2025-01-01T00:00:00Z'
      }
    };
    
    expect(isDeprecatedRemoval(change, mockConfig)).toBe(true);
  });
  
  test('should not detect non-deprecated removal', () => {
    const change: SchemaChange = {
      type: 'remove',
      path: ['components', 'schemas', 'User', 'properties', 'activeField'],
      oldValue: {
        type: 'string'
      }
    };
    
    expect(isDeprecatedRemoval(change, mockConfig)).toBe(false);
  });
  
  test('should only check removal changes', () => {
    const change: SchemaChange = {
      type: 'add',
      path: ['components', 'schemas', 'User', 'properties', 'newField'],
      newValue: {
        type: 'string',
        deprecated: true
      }
    };
    
    expect(isDeprecatedRemoval(change, mockConfig)).toBe(false);
  });
});