import { BehaviorSubject, Observable } from 'rxjs';

/**
 * Generic state subject wrapper that provides a simplified API
 * for state management with BehaviorSubject.
 *
 * Reduces boilerplate for the common pattern:
 *   private xxxSubject = new BehaviorSubject<T>(initial);
 *   xxx$ = this.xxxSubject.asObservable();
 *   get xxx(): T { return this.xxxSubject.value; }
 */
export class StateSubject<T> {
  private subject: BehaviorSubject<T>;

  constructor(initialValue: T) {
    this.subject = new BehaviorSubject<T>(initialValue);
  }

  /** Observable for subscribing to state changes */
  get $(): Observable<T> {
    return this.subject.asObservable();
  }

  /** Current state value */
  get value(): T {
    return this.subject.value;
  }

  /** Update the state to a new value */
  set(value: T): void {
    this.subject.next(value);
  }

  /** Update state by applying a transform function */
  update(fn: (current: T) => T): void {
    this.subject.next(fn(this.subject.value));
  }

  /** Reset to initial value */
  reset(initialValue: T): void {
    this.subject.next(initialValue);
  }
}

/**
 * Specialized state subject for object states with partial updates.
 * Allows updating only specific properties of the state object.
 */
export class ObjectStateSubject<T extends object> extends StateSubject<T> {
  private initialState: T;

  constructor(initialState: T) {
    super(initialState);
    this.initialState = initialState;
  }

  /** Update specific properties of the state */
  patch(partial: Partial<T>): void {
    this.update((current) => ({ ...current, ...partial }));
  }

  /** Reset to initial state */
  resetToInitial(): void {
    this.reset(this.initialState);
  }
}
